#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo ===============================================================================================
echo "## generate mbtiles with planet dump"  # TODO: use diff update
echo -----------------------------------------------------------------------------------------------
cd openmaptiles

mkdir -p data
rm -f data/belarus.osm.pbf
rm -f data/belarus.bbox
rm -f data/planet.osm.pbf
rm -f data/planet.bbox
ln -f ../tiledata/planet-latest.osm.pbf data/planet.osm.pbf
sed -r 's/MAX_ZOOM=.+$/MAX_ZOOM=14/g' .env > .env.tmp && mv .env.tmp .env
sed -r 's/#? *MID_ZOOM=.+$/MID_ZOOM=7/g' .env > .env.tmp && mv .env.tmp .env
sed -r "s/MAX_PARALLEL_PSQL=.+$/MAX_PARALLEL_PSQL=$(getconf _NPROCESSORS_ONLN)/g" .env > .env.tmp && mv .env.tmp .env
sed -r "s/COPY_CONCURRENCY=.+$/COPY_CONCURRENCY=$(getconf _NPROCESSORS_ONLN)/g" .env > .env.tmp && mv .env.tmp .env
sed -r 's,#?- layers/building/building.yaml$,#- layers/building/building.yaml,g' \
  openmaptiles.yaml > openmaptiles.yaml.tmp && mv openmaptiles.yaml.tmp openmaptiles.yaml
sed -r 's,#?- layers/housenumber/housenumber.yaml$,#- layers/housenumber/housenumber.yaml,g' \
  openmaptiles.yaml > openmaptiles.yaml.tmp && mv openmaptiles.yaml.tmp openmaptiles.yaml
sed -r 's,#?- layers/poi/poi.yaml$,#- layers/poi/poi.yaml,g' \
  openmaptiles.yaml > openmaptiles.yaml.tmp && mv openmaptiles.yaml.tmp openmaptiles.yaml
echo "-180.0,-85.0511,180.0,85.0511" > data/planet.bbox
./quickstart.sh planet
make destroy-db
mv data/tiles.mbtiles ../tiledata/planet.mbtiles

cd ..
