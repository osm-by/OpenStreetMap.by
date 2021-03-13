#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset


echo ===============================================================================================
echo "## prepare env"
echo -----------------------------------------------------------------------------------------------
. venv/bin/activate
. .env
mkdir -p testdata


echo ===============================================================================================
echo "## update styles (if not exists)"
echo -----------------------------------------------------------------------------------------------
cd tiledata

if [ ! -f "styles/bright/style.json.gz" ] ; then
    mkdir -p styles
    cd styles

    mkdir -p bright
    cd bright
    rm -f *.zip
    wget https://github.com/openmaptiles/osm-bright-gl-style/releases/download/v1.9/v1.9.zip
    unzip -o *.zip
    rm -f *.zip
    cp style-local.json style.json
    sed -i "s,mbtiles://{v3},$SITE/data/v3.json," style.json
    sed -i "s,{styleJsonFolder}/sprite,$SITE/styles/${PWD##*/}/sprite," style.json
    sed -i "s,{fontstack}/{range}.pbf,$SITE/fonts/{fontstack}/{range}.pbf," style.json
    patch style.json < ../../../tileserver-gl/osm-bright-gl-style.json.diff
    gzip -kf9 *.json
    cd ..

    cd ..
    echo "styles updated"
else
    echo "styles up to date, skipped"
fi

cd ..


echo ===============================================================================================
echo "## update fonts (if not exists)"
echo -----------------------------------------------------------------------------------------------
cd tiledata

if [ ! -f "fonts/Noto Sans Regular/0-255.pbf.gz" ] ; then
    mkdir -p fonts
    cd fonts
    rm -f *.zip
    wget https://github.com/openmaptiles/fonts/releases/download/v2.0/v2.0.zip
    unzip -o *.zip
    rm -f *.zip
    gzip -rkf9 .
    cd ..
    echo "fonts updated"
else
    echo "fonts up to date, skipped"
fi

cd ..


echo ===============================================================================================
echo "## download latest belarus osm dump"
echo -----------------------------------------------------------------------------------------------
cd tiledata

rm -f belarus-latest.osm.pbf
wget https://download.geofabrik.de/europe/belarus-latest.osm.pbf

cd ..


echo ===============================================================================================
echo "## update postgis database with belarus dump"  # TODO: use diff update
echo -----------------------------------------------------------------------------------------------
cd tiledata

docker-compose up -d postgis
sleep 5
POSTGRES_HOST_DOCKER=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'\
 openstreetmapby_postgis_1)
PGPASSWORD=$POSTGRES_PASSWORD psql \
  -h $POSTGRES_HOST_DOCKER -p $POSTGRES_POST -U $POSTGRES_USER -d $POSTGRES_DB \
  -c "CREATE EXTENSION IF NOT EXISTS hstore"
PGPASSWORD=$POSTGRES_PASSWORD osm2pgsql \
  -H $POSTGRES_HOST_DOCKER -P $POSTGRES_POST -U $POSTGRES_USER -d $POSTGRES_DB \
  -m -j -G -x --hstore-add-index -C 10000 -S ../osm2pgsql/osm2pgsql.style belarus-latest.osm.pbf

cd ..


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
sed -i -r 's/MAX_ZOOM=.+$/MAX_ZOOM=14/g' .env
make generate-bbox-file
./quickstart.sh belarus
mv data/tiles.mbtiles ../tiledata/belarus.mbtiles

cd ..


echo ===============================================================================================
echo "## reuse imported natural earth data to generate observer planet mbtiles"
echo -----------------------------------------------------------------------------------------------
cd openmaptiles

rm -f data/belarus.osm.pbf
rm -f data/belarus.bbox
rm -f data/planet.osm.pbf
rm -f data/planet.bbox
ln -f ../tiledata/belarus-latest.osm.pbf data/planet.osm.pbf
sed -i -r 's/MAX_ZOOM=.+$/MAX_ZOOM=4/g' .env
make start-db
make generate-tiles
make stop-db
mv data/tiles.mbtiles ../tiledata/planet.mbtiles

cd ..


echo ===============================================================================================
echo "## unpack belarus mbtiles to file system"
echo -----------------------------------------------------------------------------------------------
cd tiledata

mkdir -p belarus/data/v3
python ../updater/unpack_mbtiles.py belarus.mbtiles belarus/data/v3

cd ..


echo ===============================================================================================
echo "## unpack planet mbtiles to file system"
echo -----------------------------------------------------------------------------------------------
cd tiledata

mkdir -p planet/data/v3
python ../updater/unpack_mbtiles.py planet.mbtiles planet/data/v3

cd ..


echo ===============================================================================================
echo "## update tile data info (if not exists)"
echo -----------------------------------------------------------------------------------------------
if [ ! -f "tiledata/data/v3.json.gz" ] ; then
  docker-compose up -d tileserver
  sleep 5
  TILESERVER_HOST_DOCKER=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}'\
   openstreetmapby_tileserver_1)
fi
cd tiledata

if [ ! -f "data/v3.json.gz" ] ; then
    mkdir -p data
    cd data
    rm -f v3.json*
    wget http://$TILESERVER_HOST_DOCKER:8081/data/v3.json
    sed -i "s,http://$TILESERVER_HOST_DOCKER:8081/data/v3/{z}/{x}/{y}.pbf,$SITE/data/v3/{z}/{x}/{y}.pbf," v3.json
    gzip -f9 v3.json
    cd ..
    echo "tile data info updated"
else
    echo "tile data info up to date, skipped"
fi

cd ..
docker-compose stop tileserver
