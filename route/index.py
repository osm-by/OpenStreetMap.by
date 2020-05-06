#!/usr/bin/python
# -*- coding: utf-8 -*-
import GeoIP
import json
import os
import web
import sys
import psycopg2
import re

web.config.debug = False

from web.contrib.template import render_cheetah

gosmore_web = "http://2.osmosnimki.ru/route/api/dev/?v=foot&format=json&via="
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
  
def postgis_query_geojson(query, geomcolumn="way"):
  #try:
    database_connection = psycopg2.connect(pg_database)
    database_cursor = database_connection.cursor()
    database_cursor.execute(query)
    names = [q[0] for q in database_cursor.description]
    polygons = []
    for row in database_cursor.fetchall():
      geom = dict(map(None,names,row))
      for t in list(geom.keys()):
        if not geom[t]:
          del geom[t]
      geojson = json.loads(geom[geomcolumn])
      del geom[geomcolumn]
      if geojson["type"] == "GeometryCollection":
        continue
      prop = {}
      for k,v in geom.items():
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

def face_main(data):
  content_type = "text/javascript"
  a = ""
  locale = data.get("locale","be")
  if locale not in ('en','ru','be'):
    locale = "be"
  via = data["via"]
  
  
  

  return OK, content_type, a


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()                                                    # standalone run


application = web.application(urls, globals()).wsgifunc()        # mod_wsgi



