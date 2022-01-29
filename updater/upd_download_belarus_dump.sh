#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo ===============================================================================================
echo "## download latest belarus osm dump"
echo -----------------------------------------------------------------------------------------------
cd tiledata

wget --backups=1 -N https://download.geofabrik.de/europe/belarus-latest.osm.pbf
rm -f belarus-latest.osm.pbf.1

cd ..
