#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo ===============================================================================================
echo "## download latest planet osm dump"
echo -----------------------------------------------------------------------------------------------
cd tiledata

rm -f planet-latest.osm.pbf
wget https://planet.osm.org/pbf/planet-latest.osm.pbf

cd ..
