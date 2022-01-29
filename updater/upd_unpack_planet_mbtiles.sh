#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo ===============================================================================================
echo "## unpack planet mbtiles to file system"
echo -----------------------------------------------------------------------------------------------
cd tiledata

mkdir -p planet/data/v3
python3 ../updater/unpack_mbtiles.py planet.mbtiles planet/data/v3

cd ..
