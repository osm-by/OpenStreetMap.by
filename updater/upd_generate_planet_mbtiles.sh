#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo ===============================================================================================
echo "## reuse imported natural earth data to generate observer planet mbtiles"
echo -----------------------------------------------------------------------------------------------
cd openmaptiles

rm -f data/belarus.osm.pbf
rm -f data/belarus.bbox
rm -f data/planet.osm.pbf
rm -f data/planet.bbox
ln -f ../tiledata/belarus-latest.osm.pbf data/planet.osm.pbf
sed -r 's/MAX_ZOOM=.+$/MAX_ZOOM=4/g' .env > .env.tmp && mv .env.tmp .env
make start-db
make generate-tiles
make stop-db
mv data/tiles.mbtiles ../tiledata/planet.mbtiles

cd ..
