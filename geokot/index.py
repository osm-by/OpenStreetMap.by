#!/usr/bin/python
# -*- coding: utf-8 -*-
import GeoIP
import json
import os
import web
import sys
import psycopg2
import urllib
import urllib2
import re

reload(sys)
sys.setdefaultencoding("utf-8")          # a hack to support UTF-8

from lxml import etree

web.config.debug = False

from web.contrib.template import render_cheetah




pg_database = "dbname=gis user=gis"

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

def geocoder_describe((lon,lat), zoom, locale):
  descr = ()
  #try:
  if locale == "en":
    namestring = """COALESCE("name:en","int_name", replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(translate("name",'абвгдезиклмнопрстуфьАБВГДЕЗИКЛМНОПРСТУФЬ','abvgdeziklmnoprstuf’ABVGDEZIKLMNOPRSTUF’'),'х','kh'),'Х','Kh'),'ц','ts'),'Ц','Ts'),'ч','ch'),'Ч','Ch'),'ш','sh'),'Ш','Sh'),'щ','shch'),'Щ','Shch'),'ъ','”'),'Ъ','”'),'ё','yo'),'Ё','Yo'),'ы','y'),'Ы','Y'),'э','·e'),'Э','E'),'ю','yu'),'Ю','Yu'),'й','y'),'Й','Y'),'я','ya'),'Я','Ya'),'ж','zh'),'Ж','Zh')) AS name"""
  else:
    namestring = 'COALESCE("name:'+locale+'", "name") AS name'
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
    order by admin_level;"""%(namestring, lon, lat)
    database_cursor.execute(req)
    descr = database_cursor.fetchall()
    descr = [(i[0],i[1],json.loads(i[2])) for i in descr]
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
    ;"""%(namestring, lon, lat)
      database_cursor.execute(req)
      descr.extend([(i[0],i[1],json.loads(i[2])) for i in database_cursor.fetchall()])



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
    limit 1;"""%(namestring, lon, lat)
      database_cursor.execute(req)
      descr.extend([(i[0],i[1],json.loads(i[2])) for i in database_cursor.fetchall()])      

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
       
         ST_Intersects(way, ST_Buffer(ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913),10))
         and building is not null
         -- and "addr:street" is not NULL
         and "addr:housenumber" is not NULL
    limit 1;"""%(namestring, lon, lat)
      database_cursor.execute(req)
      buildings = database_cursor.fetchall()
      descr.extend([(i[0],i[1],json.loads(i[2]),i[3]) for i in buildings])

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
    limit 1;"""%(namestring, namestring, lon, lat)
      database_cursor.execute(req)
      descr.extend([(i[0],i[1],json.loads(i[2])) for i in database_cursor.fetchall()])      

  
  dd = []
  names = set()
  for i in descr:
    if i[1] not in names:
      dd.append(i)
      names.add(i[1])
  #except:
  #  pass
  return dd
  
def postgis_query_geojson(query, geomcolumn="way"):
  #try:
    database_connection = psycopg2.connect(pg_database)
    database_cursor = database_connection.cursor()
    database_cursor.execute(query)
    names = [q[0] for q in database_cursor.description]
    polygons = []
    for row in database_cursor.fetchall():
      geom = dict(map(None,names,row))
      for t in geom.keys():
        if not geom[t]:
          del geom[t]
      geojson = json.loads(geom[geomcolumn])
      del geom[geomcolumn]
      if geojson["type"] == "GeometryCollection":
        continue
      prop = {}
      for k,v in geom.iteritems():
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
  #except:
  #  return []


def geocoder_geocode(text,(lon,lat)):
  descr = ()
  #try:
  itags = '"addr:street", "addr:housenumber", "name", "name:ru", "name:be", "place", "shop", "amenity", "ref", "admin_level", "osm_id"'
  countlimit = 20
  if True:
    
    text = text.replace("\\", "\\\\").strip()
    text = text.replace("'", "\\'")
    if "котярин дом" in text.lower():
      text = "партизанский 107"
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
    order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;"""%(itags, text, text, text, lon, lat, countlimit)

    descr = postgis_query_geojson(req)
    if descr:
      return descr
    if True: ## here was check for " " in text, but it didn't allow streets to be found
      # text is complicated - needs split
      text = text.replace(".", ". ")
      text = text.replace("ё", "е")
      text = text.lower().split()
      rustreets = dict([(' ' + unicode(line).lower().split('#')[0].strip().replace('ё','е') + ' ', unicode(line).split('#')[0].strip()) for line in open("/srv/www/openstreetmap.by/htdocs/ru.txt","r")])
      cities = dict([(' ' + unicode(line).lower().strip().replace('ё','е') + ' ', unicode(line).strip()) for line in open("/srv/www/openstreetmap.by/htdocs/cities.txt","r")])
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

        "пер.": "переулок",
        "переулок": "переулок",
        "п-к": "переулок",
        
        "пр": "проезд",
        "пр-д": "проезд",
        "проезд": "проезд",
        
        "ш.": "шоссе",
        "шос.": "шоссе",
        "шоссе": "шоссе",
        }
      for k,v in status_full.items():
        del status_full[k]
        status_full[unicode(k)] = unicode(v)
      for word in text:
        word = word.strip(",").strip(".").lower()
        if not word:
          continue
        if word[0].isdigit() or ((word not in status_full) and (len(word)<=2)):
          hnos.append(word)
        elif word in status_full:
          streetstatuses.add(status_full[word])
          continue
        if (word not in status_full) and (len(word)>2):
          found = False
          ## Checking cities
          for k,v in cities.iteritems():
            if (' ' + word + ' ') in k:
              citycandidates[k] = v
              found = True
              # no inexact substring checks - please write names fully

          ## Checking streets
          for k,v in rustreets.iteritems():
            if (' ' + word + ' ') in k:
              candidates[k] = v
              found = True
          if not found:
            for k,v in rustreets.iteritems():
              if word in k:
                candidates[k] = v
      if not candidates and not citycandidates:
        return []

      wherecities = ""
      sqlcities = ""
      if citycandidates:
        sqlcities = "("+ ", ".join(["E'"+v.replace("\\", "\\\\").replace("'", "\\'")+"'" for k,v in citycandidates.iteritems()]) + ")"
        wherecities = "and way && (select ST_Collect(ST_Buffer(way,0.00001)) from planet_osm_polygon where (place in ('city', 'town', 'village', 'hamlet', 'locality') or admin_level in ('4','8','9','10')) and (name in "+sqlcities+")) and ST_Intersects(ST_Buffer(way,0.00001),(select ST_Buffer(ST_Collect(way),0) from planet_osm_polygon where (place in ('city', 'town', 'village', 'hamlet', 'locality') or admin_level in ('4','8','9','10')) and (name in "+sqlcities+"))) "

      if streetstatuses:
        for status in streetstatuses:
          if status in "|".join(candidates.keys()):
            for can in candidates.keys():
              if status not in can:
                del candidates[can]
      if len(candidates) > 20:
        for hno in list(hnos):
          if hno in "|".join(candidates.keys()):
            for can in candidates.keys():
              if hno not in can:
                del candidates[can]
            hnos.remove(hno)
      can = set()
      for k,candidate in candidates.iteritems():
        can.add(candidate)
        can.add(candidate.lower())
        can.add(candidate.replace("проспект", "просп."))
        can.add(candidate.replace("улица", "ул."))
      escaped_can = "(" + ", ".join(["E'"+a.replace("\\", "\\\\").replace("'", "\\'")+"'" for a in can]) + ")"
      wherestreets = '"addr:street" is NULL and'
      if can:
        wherestreets = '"addr:street" in %s and' % escaped_can
      escaped_hnos = "(" + ", ".join(["E'"+a.replace("\\", "\\\\").replace("'", "\\'")+"'" for a in hnos]) + ")"
      
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
order by distance limit %s;"""%(itags, lon, lat, wherestreets, escaped_hnos, wherecities, itags, lon, lat, wherestreets, escaped_hnos, wherecities, countlimit)
        descr = postgis_query_geojson(req)
        if descr:
          return descr
        # then, try buildings that start with that number
        like_hnos = "(" + " or ".join(["\"addr:housenumber\" ILIKE E'"+a.replace("\\", "\\\\").replace("'", "\\'")+"%'" for a in hnos]) + ")"
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
    order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;"""%(itags, escaped_can, like_hnos, wherecities, lon, lat, countlimit)
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
order by distance limit %s;"""%(itags, lon, lat, escaped_can, escaped_hnos, '', itags, lon, lat, escaped_can, escaped_hnos, "", countlimit)
        descr = postgis_query_geojson(req)
        if descr:
          return descr
        # then, try buildings that start with that number
        like_hnos = "(" + " or ".join(["\"addr:housenumber\" ILIKE E'"+a.replace("\\", "\\\\").replace("'", "\\'")+"%'" for a in hnos]) + ")"
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
    order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;"""%(itags, escaped_can, like_hnos, "", lon, lat, countlimit)
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
  order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;"""%(itags, escaped_can, escaped_can, wherecities, lon, lat, countlimit)
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
  order by ST_Distance(way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;"""%(itags, sqlcities, lon, lat, countlimit)        
        descr = postgis_query_geojson(req)
        if descr:
          return descr
  return descr



def organisations_around_point((lon,lat), locale):
  if locale == "en":
    namestring = """COALESCE(p."name:en",p."int_name", replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(replace(translate(p."name",'абвгдезиклмнопрстуфьАБВГДЕЗИКЛМНОПРСТУФЬ','abvgdeziklmnoprstuf’ABVGDEZIKLMNOPRSTUF’'),'х','kh'),'Х','Kh'),'ц','ts'),'Ц','Ts'),'ч','ch'),'Ч','Ch'),'ш','sh'),'Ш','Sh'),'щ','shch'),'Щ','Shch'),'ъ','”'),'Ъ','”'),'ё','yo'),'Ё','Yo'),'ы','y'),'Ы','Y'),'э','·e'),'Э','E'),'ю','yu'),'Ю','Yu'),'й','y'),'Й','Y'),'я','ya'),'Я','Ya'),'ж','zh'),'Ж','Zh')) AS name"""
  else:
    namestring = 'COALESCE(p."name:'+locale+'", p."name") AS name'
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
  order by ST_Distance(p.way, ST_Transform(ST_GeomFromText('POINT(%f %s)',4326),900913)) limit %s;"""%(namestring, lon, lat,lon, lat, lon, lat, countlimit)

  descr = postgis_query_geojson(req)
  if descr:
    return descr
  


def face_main(data):
  content_type = "text/html"
  a = ""
  locale = data.get("locale","be")
  if locale not in ('en','ru','be'):
    locale = "be"
  if data.get('request') == 'describe':
    content_type = "text/javascript"
    lat = float(data["lat"])
    lon = float(data["lon"])
    zoom = float(data.get("zoom", 10))
    a = {}
    a["breadcrumbs"] = geocoder_describe((lon,lat), zoom, locale)
    a = json.dumps(a, ensure_ascii=False)
  elif data.get('request') == 'geocode':
    content_type = "text/javascript"
    lat = float(data.get("lat", 53.9))
    lon = float(data.get("lon", 27.5))
    text = data.get("text",'Minsk')
    a = {}
    a["results"] = geocoder_geocode(text,(lon,lat))
    try:
      logfile = open('/srv/www/openstreetmap.by/htdocs/req.txt', "a")
      print >> logfile, len(a["results"]), lon, lat, text
      logfile.close()
      if len(a["results"]) == 0:
        logfile = open('/srv/www/openstreetmap.by/htdocs/notfound.txt', "a")
        print >> logfile, len(a["results"]), lon, lat, text
        logfile.close()
    except:
      pass
    a = json.dumps(a, ensure_ascii=False)
  elif data.get('request') == 'click_about':
    content_type = "text/javascript"
    lat = float(data.get("lat", 53.9))
    lon = float(data.get("lon", 27.5))
    locale = data.get("locale","be")
    if locale not in ('en','ru','be'):
      locale = "be"
    a = {}
    a["results"] = organisations_around_point((lon,lat), locale)
    a["coords"] = (lon, lat)
    a = json.dumps(a, ensure_ascii=False)

  return OK, content_type, a


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()                                                    # standalone run


application = web.application(urls, globals()).wsgifunc()        # mod_wsgi



