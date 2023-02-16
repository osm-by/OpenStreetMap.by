#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo ===============================================================================================
echo "## unpack belarus mbtiles to file system"
echo -----------------------------------------------------------------------------------------------
cd tiledata

mkdir -p belarus/data/v3
python3 ../updater/unpack_mbtiles.py belarus.mbtiles belarus/data/v3 ../updater/belarus.poly

cd ..
