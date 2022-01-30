#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo ===============================================================================================
echo "## generate mbtiles with belarus dump"  # TODO: use diff update
echo -----------------------------------------------------------------------------------------------
cd openmaptiles

mkdir -p data
rm -f data/belarus.osm.pbf
rm -f data/belarus.bbox
rm -f data/planet.osm.pbf
rm -f data/planet.bbox
ln -f ../tiledata/belarus-latest.osm.pbf data/belarus.osm.pbf
sed -r 's/MAX_ZOOM=.+$/MAX_ZOOM=14/g' .env > .env.tmp && mv .env.tmp .env
make generate-bbox-file
./quickstart.sh belarus
mv data/tiles.mbtiles ../tiledata/belarus.mbtiles

cd ..
