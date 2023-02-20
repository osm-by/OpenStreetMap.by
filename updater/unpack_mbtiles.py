import math
import os
import sqlite3
import string
import sys
from itertools import product

import shapely.geometry


MBTILES = sys.argv[1]
OUT_FOLDER = os.path.abspath(sys.argv[2])
BORDER_FILE = sys.argv[3] if len(sys.argv) > 3 else None
BORDER = None
if BORDER_FILE is not None:
    with open(BORDER_FILE) as h:
        coords = []
        for l in h:
            if l.strip() and l.startswith('   '):
                x, y = l.strip().split('   ')
                coords.append((float(x), float(y)))
        BORDER = shapely.geometry.Polygon(coords)
SUFFIX = '.gz'
SQL_TEMPLATE = """
SELECT
    map.zoom_level AS zoom_level,
    map.tile_column AS tile_column,
    map.tile_row AS tile_row,
    map.tile_id AS tile_id,
    images.tile_data AS tile_data
FROM map
JOIN images ON images.tile_id = map.tile_id
WHERE images.tile_id > '{0}' AND images.tile_id < '{0}|'
"""

conn = sqlite3.connect(MBTILES)
cursor = conn.cursor()
folders = set()


def tile_to_lon(x, z):
    return x / 2.0 ** z * 360.0 - 180


def tile_to_lat(y, z):
    n = math.pi - 2.0 * math.pi * y / 2.0 ** z
    return math.degrees(math.atan(math.sinh(n)))


def skip(zoom_level, tile_column, tile_row, border):
    """Used to avoid planet tiles overriding on border"""
    if border is None:
        return False
    n = tile_to_lat(tile_row, zoom_level)
    s = tile_to_lat(tile_row + 1, zoom_level)
    w = tile_to_lon(tile_column, zoom_level)
    e = tile_to_lon(tile_column + 1, zoom_level)
    bbox = shapely.geometry.box(w, s, e, n)
    return not border.contains(bbox)


for prefix in product(*[string.hexdigits.lower()] * 2):
    duplicates = {}
    sql = SQL_TEMPLATE.format(''.join(prefix))
    for zoom_level, tile_column, tile_row, tile_hash, tile_data in cursor.execute(sql):
        reversed_tile_row = 2 ** zoom_level - tile_row - 1
        if skip(zoom_level, tile_column, reversed_tile_row, BORDER):
            continue
        file_name = os.path.join(
            OUT_FOLDER, str(zoom_level), str(tile_column), str(reversed_tile_row) + '.pbf' + SUFFIX
        )
        parent_dir = os.path.dirname(file_name)
        if parent_dir not in folders:
            os.makedirs(parent_dir, exist_ok=True)
            folders.add(parent_dir)
        if os.path.exists(file_name):
            os.remove(file_name)  # unlink hardlinks
        if tile_data not in duplicates:
            with open(file_name, 'wb') as handler:
                handler.write(tile_data)
            duplicates[tile_hash] = file_name
        else:
            try:
                os.link(duplicates[tile_hash], file_name)
            except OSError:
                # in case too many links error appears
                with open(file_name, 'wb') as handler:
                    handler.write(tile_data)
                duplicates[tile_hash] = file_name


conn.close()
