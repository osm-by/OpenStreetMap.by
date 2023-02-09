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
sed -r 's,#?- layers/building/building.yaml$,- layers/building/building.yaml,g' \
  openmaptiles.yaml > openmaptiles.yaml.tmp && mv openmaptiles.yaml.tmp openmaptiles.yaml
sed -r 's,#?- layers/housenumber/housenumber.yaml$,- layers/housenumber/housenumber.yaml,g' \
  openmaptiles.yaml > openmaptiles.yaml.tmp && mv openmaptiles.yaml.tmp openmaptiles.yaml
sed -r 's,#?- layers/poi/poi.yaml$,- layers/poi/poi.yaml,g' \
  openmaptiles.yaml > openmaptiles.yaml.tmp && mv openmaptiles.yaml.tmp openmaptiles.yaml
sed -r 's,#?- layers/transportation_name/transportation_name.yaml$,- layers/transportation_name/transportation_name.yaml,g' \
  openmaptiles.yaml > openmaptiles.yaml.tmp && mv openmaptiles.yaml.tmp openmaptiles.yaml
make generate-bbox-file
./quickstart.sh belarus
make destroy-db
mv data/tiles.mbtiles ../tiledata/belarus.mbtiles

cd ..
