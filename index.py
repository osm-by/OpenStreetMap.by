#!/usr/bin/python
# -*- coding: utf-8 -*-
import GeoIP
import json
import os
import web
import sys
import psycopg2
import re
import redis
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

web.config.debug = False

from web.contrib.template import render_cheetah

GeoIpCache = GeoIP.open('GeoLiteCity.dat', GeoIP.GEOIP_MEMORY_CACHE)
pg_database = f"host={os.environ['POSTGRES_HOST']} dbname={os.environ['POSTGRES_DB']} user={os.environ['POSTGRES_USER']} password={os.environ['POSTGRES_PASSWORD']}"

LOCALES = ['be', 'be-tarask', 'ru', 'en', 'none']

OK = 200
ERROR = 500


def handler():
    """
    A handler for web.py.
    """
    data = web.input()
    resp, ctype, content = face_main(data)
    web.header('Content-type', ctype)
    return content


urls = (
    '/(.*)', 'mainhandler'
)


class mainhandler:
    def GET(self, crap):
        return handler()

    def POST(self, crap):
        return handler()


def get_available_layers(lon_lat):
    lon, lat = lon_lat
    layers = ["osm"]
    return layers


def geocoder_describe(lon_lat, zoom, locale):
    lon, lat = lon_lat
    descr = ()
    # try:
    if locale == "en":
        namestring = """COALESCE("name:en","int_name", replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(translate("name",'абвгдезиклмнопрстуфьАБВГДЕЗИКЛМНОПРСТУФЬ','abvgdeziklmnoprstuf’ABVGDEZIKLMNOPRSTUF’'),'х','kh'),'Х','Kh'),'ц','ts'),'Ц','Ts'),'ч','ch'),'Ч','Ch'),'ш','sh'),'Ш','Sh'),'щ','shch'),'Щ','Shch'),'ъ','”'),'Ъ','”'),'ё','yo'),'Ё','Yo'),'ы','y'),'Ы','Y'),'э','·e'),'Э','E'),'ю','yu'),'Ю','Yu'),'й','y'),'Й','Y'),'я','ya'),'Я','Ya'),'ж','zh'),'Ж','Zh')) AS name"""
    else:
        namestring = 'COALESCE("name:' + locale + '", "name") AS name'
    if True:
        database_connection = psycopg2.connect(pg_database)
        database_cursor = database_connection.cursor()
        req = """
    select
        admin_level,
        %s,
        ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0))
    from planet_osm_polygon
    where
       (
         ST_Intersects(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913))
         and admin_level in ('1','2','3','4','5','6','7','8'))
         and ("name:ru" is not NULL or name is not NULL)
         and boundary = 'administrative'
    order by admin_level;""" % (namestring, lon, lat)
        database_cursor.execute(req)
        descr = database_cursor.fetchall()
        descr = [(i[0], i[1], json.loads(i[2])) for i in descr]
        if zoom > 10:
            req = """
    select
        "place" as admin_level,
        %s,
        ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0))
    from planet_osm_polygon
    where
         ST_Intersects(way, ST_Buffer(ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913),10))
         and place in ('city', 'town', 'village', 'hamlet')
         and ("name:ru" is not NULL or name is not NULL)
    ;""" % (namestring, lon, lat)
            database_cursor.execute(req)
            descr.extend([(i[0], i[1], json.loads(i[2])) for i in database_cursor.fetchall()])

        if zoom > 12:
            req = """
    select
        'park' as admin_level,
        %s,
        ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0))
    from planet_osm_polygon p
    where
         ST_Intersects(way, ST_Buffer(ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913),10))
         and leisure in ('park', 'square', 'garden')
         and ("name:ru" is not NULL or name is not NULL)
    limit 1;""" % (namestring, lon, lat)
            database_cursor.execute(req)
            descr.extend([(i[0], i[1], json.loads(i[2])) for i in database_cursor.fetchall()])

        buildings = False
        if zoom > 13:
            req = """
    select
        'building' as admin_level,
        coalesce(
          coalesce((select %s from planet_osm_line l where p."addr:street"=l."name" order by ST_Distance(p.way,l.way) limit 1), "addr:street") || ', ' || "addr:housenumber",
          "addr:housenumber"
        )
          ,
        ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0)),
        "addr:housenumber"
    from planet_osm_polygon p
    where
       
         ST_Intersects(way, ST_Buffer(ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913),100))
         and building is not null
         -- and "addr:street" is not NULL
         and "addr:housenumber" is not NULL
    order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913))
    limit 1;""" % (namestring, lon, lat, lon, lat)
            database_cursor.execute(req)
            buildings = database_cursor.fetchall()
            descr.extend([(i[0], i[1], json.loads(i[2]), i[3]) for i in buildings])

        if (not buildings) and zoom > 13:
            req = """
    select
        "highway" as admin_level,
        COALESCE( (select %s) || ' (' || ref || ')', (select %s), ref),
        ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0))
    from planet_osm_line
    where
         ST_DWithin(way, 
            ST_Transform(
              ST_GeomFromText('POINT(%f %s)',4326),
              900913),
            50
          )
         and highway is not NULL
         and ("name:ru" is not NULL or name is not NULL or ref is not NULL)
    limit 1;""" % (namestring, namestring, lon, lat)
            database_cursor.execute(req)
            descr.extend([(i[0], i[1], json.loads(i[2])) for i in database_cursor.fetchall()])

    dd = []
    names = set()
    for i in descr:
        if i[1] not in names:
            dd.append(i)
            names.add(i[1])
    # except:
    #  pass
    return dd


def postgis_query_geojson(query, geomcolumn="way"):
    # try:
    database_connection = psycopg2.connect(pg_database)
    database_cursor = database_connection.cursor()
    try:
        database_cursor.execute(query)
    except:
        print("QUERY FAILURE: ", query, file=sys.stderr)
        sys.stderr.flush()
    names = [q[0] for q in database_cursor.description]
    polygons = []
    for row in database_cursor.fetchall():
        geom = dict(zip(names, row))
        for t in list(geom.keys()):
            if not geom[t]:
                del geom[t]
        geojson = json.loads(geom[geomcolumn])
        del geom[geomcolumn]
        if geojson["type"] == "GeometryCollection":
            continue
        prop = {}
        for k, v in geom.items():
            prop[k] = v
            try:
                if int(v) == float(v):
                    prop[k] = int(v)
                else:
                    prop[k] = float(v)
                if str(prop[k]) != v:  # leading zeros etc.. should be saved
                    prop[k] = v
            except:
                pass
        geojson["properties"] = prop
        polygons.append(geojson)
    return polygons
    # except:
    #  return []


def geocoder_geocode(text, lon_lat):
    lon, lat = lon_lat
    descr = ()
    # try:
    itags = '"addr:street", "addr:housenumber", "name", "name:ru", "name:be", "place", "shop", "amenity", "ref", "admin_level", "osm_id", "building"'
    countlimit = 20
    otext = text
    if True:
        text = text.replace("\\", "\\\\").strip()
        text = text.replace("'", "\\'")
        if "котярин дом" in text.lower():
            text = "партизанский 107"

        if True:  ## here was check for " " in text, but it didn't allow streets to be found
            # text is complicated - needs split
            text = text.replace(".", ". ")
            text = text.replace(",", ", ")
            text = text.replace("ё", "е")
            text = text.lower().split()
            rustreets = dict([(' ' + str(line).lower().split('#')[0].strip().replace('ё', 'е') + ' ',
                               str(line).split('#')[0].strip()) for line in open("ru.txt", "r")])
            cities = dict(
                [(' ' + str(line).lower().strip().replace('ё', 'е') + ' ', str(line).strip()) for line in
                 open("cities.txt", "r")])
            candidates = {}
            citycandidates = {}
            hnos = []
            streetstatuses = set()
            status_full = {
                "проспект": "проспект",
                "просп": "проспект",
                "пр-т": "проспект",

                "улица": "улица",
                "ул": "улица",

                "тр-т": "тракт",
                "тракт": "тракт",

                "пер": "переулок",
                "переулок": "переулок",
                "п-к": "переулок",

                "пр": "проезд",
                "пр-д": "проезд",
                "проезд": "проезд",

                "ш": "шоссе",
                "шос": "шоссе",
                "шоссе": "шоссе",
            }
            for k, v in list(status_full.items()):
                del status_full[k]
                status_full[str(k)] = str(v)
            for word in text:
                word = word.strip(",").strip(".").lower()
                if not word:
                    continue
                if word[0].isdigit() or ((word not in status_full) and (len(word) <= 2)):
                    hnos.append(word)
                    continue
                elif word in status_full:
                    streetstatuses.add(status_full[word])
                    continue
                if (word not in status_full) and (len(word) > 2):
                    found = False
                    ## Checking cities
                    for k, v in cities.items():
                        if (' ' + word + ' ') in k:
                            citycandidates[k] = v
                            # found = True
                            # no inexact substring checks - please write names fully

                    ## Checking streets
                    for k, v in rustreets.items():
                        if (' ' + word + ' ') in k:
                            candidates[k] = v
                            found = True
                    if not found:
                        for k, v in rustreets.items():
                            if (' ' + word) in k:
                                candidates[k] = v
                                found = True
                    if not found:
                        for k, v in rustreets.items():
                            if word in k:
                                candidates[k] = v
            if not candidates and not citycandidates:
                return []

            wherecities = ""
            sqlcities = ""
            if citycandidates:
                sqlcities = "(" + ", ".join(["E'" + v.replace("\\", "\\\\").replace("'", "\\'") + "'" for k, v in
                                             citycandidates.items()]) + ")"
                wherecities = "and way && (select ST_Collect(ST_Buffer(way,0.00001)) from planet_osm_polygon where (place in ('city', 'town', 'village', 'hamlet', 'locality') or admin_level in ('4','8','9','10')) and (name in " + sqlcities + ")) and ST_Intersects(ST_Buffer(way,0.00001),(select ST_Buffer(ST_Collect(way),0) from planet_osm_polygon where (place in ('city', 'town', 'village', 'hamlet', 'locality') or admin_level in ('4','8','9','10')) and (name in " + sqlcities + "))) "
                # if not streetstatuses:
                # streetstatuses = ["проспект", "улица", "площадь"]
            if streetstatuses:
                for status in streetstatuses:
                    if status in "|".join(list(candidates.keys())):
                        for can in list(candidates.keys()):
                            if status not in can:
                                del candidates[can]
            if len(candidates) > 20:
                for hno in list(hnos):
                    if hno in "|".join(list(candidates.keys())):
                        for can in list(candidates.keys()):
                            if hno not in can:
                                del candidates[can]
                        hnos.remove(hno)
            can = set()
            for k, candidate in candidates.items():
                can.add(candidate)
                can.add(candidate.lower())
                can.add(candidate.replace("проспект", "просп."))
                can.add(candidate.replace("улица", "ул."))
                can.add(candidate.replace("переулок", "пер."))

            escaped_can = "(" + ", ".join(["E'" + a.replace("\\", "\\\\").replace("'", "\\'") + "'" for a in can]) + ")"
            wherestreets = '"addr:street" is NULL and'
            if can:
                wherestreets = '"addr:street" in %s and' % escaped_can

            hcan = set()
            for candidate in hnos:
                hcan.add(candidate)
                hcan.add(candidate.lower())
                hcan.add(candidate.upper())
                hcan.add(candidate.replace("к", "к "))
                hcan.add(candidate.replace("к", " к"))
                hcan.add(candidate.replace("К", " к"))

                hno_rxp = re.compile(
                    '([0-9]*)\s*([а-йл-яА-ЙЛ-Я]*)\s*,?\s*(к\.|к|корп\.|корпус)?\s*([0-9]*)\s*([а-яА-Я]*)[.]?$')
                en = "eyopakxc"
                ru = "еуоракхс"
                for i in range(0, len(en) - 1):
                    candidate = candidate.replace(en[i], ru[i])
                    hcan.add(candidate)
                p = hno_rxp.match(candidate.upper())
                if p:
                    hno = p.groups()
                    hno = [hno[0], hno[1], hno[3], hno[4]]

                    zhno = ""
                    zhno += str(hno[0]) + str(hno[1])
                    if hno[2] or hno[3]:
                        zhno += " к" + str(hno[2]) + str(hno[3])
                    hcan.add(zhno)
            hnos = list(hcan)
            escaped_hnos = "(" + ", ".join(
                ["E'" + a.replace("\\", "\\\\").replace("'", "\\'") + "'" for a in hnos]) + ")"

            if hnos:
                # trying to find buildings. first - exact hno match
                req = """
select
    %s,
    ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0)) as way,
    ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) as distance
from planet_osm_polygon
where
    (
    %s
    ("addr:housenumber" in %s)
    %s
    )
union
select
    %s,
    ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0.0005)) as way,
    ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) as distance
from planet_osm_point
where
    (
    %s
    ("addr:housenumber" in %s)
    %s
    )
order by distance limit %s;""" % (
                    itags, lon, lat, wherestreets, escaped_hnos, wherecities, itags, lon, lat, wherestreets,
                    escaped_hnos,
                    wherecities, countlimit)
                descr = postgis_query_geojson(req)
                if descr:
                    return descr
                # then, try buildings that start with that number
                like_hnos = "(" + " or ".join(
                    ["\"addr:housenumber\" ILIKE E'" + a.replace("\\", "\\\\").replace("'", "\\'") + "%'" for a in
                     hnos]) + ")"
                req = """
    select
    %s,
    ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0)) as way
    from planet_osm_polygon
    where
    (
    "addr:street" in %s and
     %s
     %s
    )
    order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;""" % (
                    itags, escaped_can, like_hnos, wherecities, lon, lat, countlimit)
                descr = postgis_query_geojson(req)
                if descr:
                    return descr
            if hnos and citycandidates:
                # failed searching for buildings in city, so retry without city.
                # trying to find buildings. first - exact hno match
                req = """
select
    %s,
    ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0)) as way,
    ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) as distance
from planet_osm_polygon
where
    (
    "addr:street" in %s and
    ("addr:housenumber" in %s)
    %s
    )
union
select
    %s,
    ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0.0005)) as way,
    ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) as distance
from planet_osm_point
where
    (
    "addr:street" in %s and
    ("addr:housenumber" in %s)
    %s
    )
order by distance limit %s;""" % (
                    itags, lon, lat, escaped_can, escaped_hnos, '', itags, lon, lat, escaped_can, escaped_hnos, "",
                    countlimit)
                descr = postgis_query_geojson(req)
                if descr:
                    return descr
                # then, try buildings that start with that number
                like_hnos = "(" + " or ".join(
                    ["\"addr:housenumber\" ILIKE E'" + a.replace("\\", "\\\\").replace("'", "\\'") + "%'" for a in
                     hnos]) + ")"
                req = """
    select
    %s,
    ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0)) as way
    from planet_osm_polygon
    where
    (
    "addr:street" in %s and
     %s
     %s
    )
    order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;""" % (
                    itags, escaped_can, like_hnos, "", lon, lat, countlimit)
                descr = postgis_query_geojson(req)
                if descr:
                    return descr

            if candidates:
                req = """
  select
  %s,
  ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0),6) as way
  from planet_osm_line
  where
  ("name" in %s or "name:en" in %s )
  %s
  order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;""" % (
                    itags, escaped_can, escaped_can, wherecities, lon, lat, countlimit)
                descr = postgis_query_geojson(req)
                if descr:
                    return descr
            if citycandidates:
                req = """
  select
  %s,
  ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0),6) as way
  from planet_osm_polygon
  where
  ("name" in %s)
  and (place in ('city', 'town', 'village', 'hamlet', 'locality') or admin_level in ('4','8','9','10'))
  order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;""" % (
                    itags, sqlcities, lon, lat, countlimit)
                descr = postgis_query_geojson(req)
                if descr:
                    return descr

        ### Exact match - last resort
        req = """
    select
        %s,
        ST_AsGeoJSON(ST_Expand(ST_Transform(way,4326),0)) as way
    from planet_osm_polygon
    where
       (
       -- "name:ru" = E'%s' or 
       name = E'%s' or 
       "name:en" = E'%s'
       )
    order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;""" % (
            itags, otext, otext, otext, lon, lat, countlimit)
        descr = postgis_query_geojson(req)
        if descr:
            return descr

    return descr


def organisations_around_point(lon_lat, locale):
    lon, lat = lon_lat
    if locale == "en":
        namestring = """COALESCE(p."name:en",p."int_name", replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(translate(p."name",'абвгдезиклмнопрстуфьАБВГДЕЗИКЛМНОПРСТУФЬ','abvgdeziklmnoprstuf’ABVGDEZIKLMNOPRSTUF’'),'х','kh'),'Х','Kh'),'ц','ts'),'Ц','Ts'),'ч','ch'),'Ч','Ch'),'ш','sh'),'Ш','Sh'),'щ','shch'),'Щ','Shch'),'ъ','”'),'Ъ','”'),'ё','yo'),'Ё','Yo'),'ы','y'),'Ы','Y'),'э','·e'),'Э','E'),'ю','yu'),'Ю','Yu'),'й','y'),'Й','Y'),'я','ya'),'Я','Ya'),'ж','zh'),'Ж','Zh')) AS name"""
    else:
        namestring = 'COALESCE(p."name:' + locale + '", p."name") AS name'
    countlimit = 100
    req = """
  select distinct
      %s,
      p."opening_hours",
      p."phone",
      p."amenity",
      p.operator,
      p.description,
      p.website,
      p.url,
      p.shop,
      p.office,
      p.tags->'craft' as craft,
      p.ref,
      p.atm,
      p.level,
      ST_AsGeoJSON(ST_Transform(p.way,4326),6) as way,
      ST_Distance(p.way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) as dist
  from planet_osm_polygon b,
       planet_osm_point p
  where
      (
      ST_Intersects(b.way, ST_Buffer(ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913),5))
      and b.building is not NULL
      and ST_DWithin(b.way, p.way, 10)
      and (p.amenity is not NULL or p.shop is not NULL or p.office is not NULL or (p.tags->'craft') is not NULL)
      )
  order by ST_Distance(p.way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;""" % (
        namestring, lon, lat, lon, lat, lon, lat, countlimit)

    descr = postgis_query_geojson(req)
    if descr:
        return descr


def i18n(aaaa):
    return web.input().get("lang")


def face_main(data):
    content_type = "text/html"
    render = render_cheetah('templates/')
    locale = data.get("lang", "be")
    userip = os.environ.get("REMOTE_ADDR", "0.0.0.0")

    if locale not in ('en', 'ru', 'be', 'be-tarask'):
        locale = "be"
    if data.get('request') == 'describe':
        content_type = "text/javascript"
        lat = float(data["lat"])
        lon = float(data["lon"])

        zoom = float(data.get("zoom", 10))
        userid = data.get("id", "none")
        r = redis.Redis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']), db=int(os.environ['REDIS_DB']))
        r.rpush("osmbyusers:" + userip + ":" + userid, json.dumps([lat, lon, zoom, locale, time.time()]))
        r.expire("osmbyusers:" + userip + ":" + userid, 3600)
        a = {"breadcrumbs": geocoder_describe((lon, lat), zoom, locale)}
        a = json.dumps(a, ensure_ascii=False)

    elif data.get('request') == 'getusersnow':
        content_type = "text/javascript"
        r = redis.Redis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']), db=int(os.environ['REDIS_DB']))
        a = r.keys("osmbyusers*")
        b = []
        for i in a:
            b.append([json.loads(j) for j in r.lrange(i, 0, 1000)])
        a = b
        a = json.dumps(a)

    elif data.get('request') == 'geocode':
        content_type = "text/javascript"
        lat = float(data.get("lat", 53.9))
        lon = float(data.get("lon", 27.5))
        text = data.get("text", 'Minsk')
        a = {"results": geocoder_geocode(text, (lon, lat))}

        try:
            logfile = open('req.txt', "a")
            print(len(a["results"]), lon, lat, text, file=logfile)
            logfile.close()
            if len(a["results"]) == 0:
                logfile = open('notfound.txt', "a")
                print(len(a["results"]), lon, lat, text, file=logfile)
                logfile.close()
        except:
            pass
        a = json.dumps(a, ensure_ascii=False)


    elif data.get('request') == 'click_about':
        content_type = "text/javascript"
        lat = float(data.get("lat", 53.9))
        lon = float(data.get("lon", 27.5))
        a = {"results": organisations_around_point((lon, lat), locale), "coords": (lon, lat)}
        a = json.dumps(a, ensure_ascii=False)

    elif data.get('request') == 'locale-tracebug':
        lang = data.get("lang", None)
        tt = data.get("lines", "|")[:-1]  # string%1|string2%3
        if (lang in LOCALES) and tt:
            r = redis.Redis(host=os.environ['REDIS_HOST'], port=int(os.environ['REDIS_PORT']), db=int(os.environ['REDIS_DB']))
            tt = [(i.split('%')[0], float(i.split('%')[1])) for i in tt.split('|')]
            for i in tt:
                r.zincrby('locale:' + lang, i[1], i[0])
        a = "ok"

    else:
        lat, lon, zoom = (0, 0, 1)
        layer = "osm"
        try:  # first try to get map postiton from URL
            lat = float(data["lat"])
            lon = float(data["lon"])
            zoom = float(data.get("zoom", 10))
        except (KeyError, ValueError):
            user_geoip = GeoIpCache.record_by_addr(userip)  # try GeoIP
            try:
                lat = user_geoip["latitude"]
                lon = user_geoip["longitude"]
            except TypeError:
                lat = 53.907169
                lon = 27.579460
            zoom = 8
        description = "OpenStreetMap Беларусь. Карта, рисуемая людьми."

        import math
        def deg2num(lat_deg, lon_deg, zoom):
            lat_rad = math.radians(lat_deg)
            n = 2.0 ** zoom
            xtile = ((lon_deg + 180.0) / 360.0 * n)
            ytile = ((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
            return (xtile, ytile)

        snippeturl = ""
        if data.get("lat"):
            offzoom = int(max(zoom - 2, 0))

            snippeturl = "http://twms.kosmosnimki.ru/?layers=osm&request=GetTile&z=%s&x=%s&y=%s&format=image/png" % (
                offzoom, deg2num(lat, lon, offzoom)[0] - .5, deg2num(lat, lon, offzoom)[1] - .5)
            try:
                description = [i[1] for i in geocoder_describe((lon, lat), zoom, locale)]
                description.reverse()
                description = ", ".join(description) + " на картах OpenStreetMap Беларусь"
                description.replace('"', '')
            except:
                pass
        a = render.index(_=i18n, locale=locale, longitude=lon, latitude=lat, zoom=zoom, description=description,
                         snippeturl=snippeturl)
        if data.get("beta"):
            a = render.indexb(_=i18n, locale=locale, longitude=lon, latitude=lat, zoom=zoom, description=description,
                              snippeturl=snippeturl)
    return OK, content_type, a


if __name__ == "__main__":
    # standalone run

    # stop listening on 0.0.0.0
    if not sys.argv[1:]:
        sys.argv.append('127.0.0.1')
    app = web.application(urls, globals())

    # serve all files as static
    def root_static(app):
        class RootMiddleware:
            def __call__(self, environ, start_response):
                path = environ.get("PATH_INFO", "")
                relpath = path[1:]  # strip leading "/" if exists
                if os.path.isfile(relpath):
                    return web.httpserver.StaticApp(environ, start_response)
                else:
                    return app(environ, start_response)

        return RootMiddleware()

    app.run(root_static)


application = web.application(urls, globals()).wsgifunc()  # mod_wsgi
