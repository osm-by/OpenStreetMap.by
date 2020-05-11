import os
import sqlite3
import sys

MBTILES = sys.argv[1]
OUT_FOLDER = os.path.abspath(sys.argv[2])
SUFFIX = '.gz'

conn = sqlite3.connect(sys.argv[1])
c = conn.cursor()

# TODO: use hash instead string value to decrease memory usage
duplicates = {}

# TODO: use iteration to decrease memory usage
for row in c.execute("SELECT zoom_level, tile_column, tile_row, tile_data FROM tiles"):
    zoom_level, tile_column, tile_row, tile_data = row
    reversed_tile_row = 2 ** zoom_level - tile_row - 1
    file_name = os.path.join(
        OUT_FOLDER, str(zoom_level), str(tile_column), str(reversed_tile_row) + '.pbf' + SUFFIX
    )
    parent_dir = os.path.dirname(file_name)
    os.makedirs(parent_dir, exist_ok=True)
    if os.path.exists(file_name):
        os.remove(file_name)  # unlink hardlinks
    if tile_data not in duplicates:
        with open(file_name, 'wb') as handler:
            handler.write(tile_data)
        duplicates[tile_data] = file_name
    else:
        os.link(duplicates[tile_data], file_name)

conn.close()
