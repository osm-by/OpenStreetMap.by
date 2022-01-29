#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo ===============================================================================================
echo "## update postgis database with belarus dump"  # TODO: use diff update
echo -----------------------------------------------------------------------------------------------
cd tiledata

sleep 5
PGPASSWORD=$POSTGRES_PASSWORD psql \
  -h $POSTGRES_HOST -p $POSTGRES_POST -U $POSTGRES_USER -d $POSTGRES_DB \
  -c "CREATE EXTENSION IF NOT EXISTS hstore"
PGPASSWORD=$POSTGRES_PASSWORD osm2pgsql \
  -H $POSTGRES_HOST -P $POSTGRES_POST -U $POSTGRES_USER -d $POSTGRES_DB \
  -v -m -j -G -x --hstore-add-index -C $OSM2PGSQL_CACHE -S ../osm2pgsql/osm2pgsql.style belarus-latest.osm.pbf

cd ..
