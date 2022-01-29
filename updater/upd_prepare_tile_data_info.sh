#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

echo ===============================================================================================
echo "## update tile data info (if not exists)"
echo -----------------------------------------------------------------------------------------------
cd tiledata

if [ ! -f "data/v3.json.gz" ] ; then
    mkdir -p data
    cd data
    rm -f v3.json*
    wget http://$TILESERVER_HOST:8081/data/v3.json
    sed "s,http://$TILESERVER_HOST:8081/data/v3/{z}/{x}/{y}.pbf,http://localhost/data/v3/{z}/{x}/{y}.pbf," v3.json \
        > v3.json.tmp && mv v3.json.tmp v3.json
    sed -r 's|"bounds":\[[-0-9.,]+\]|"bounds":[-180.0,-85.0511,180.0,85.0511]|g' v3.json \
        > v3.json.tmp && mv v3.json.tmp v3.json
    gzip -kf9 v3.json
    cd ..
    echo "tile data info updated"
else
    echo "tile data info up to date, skipped"
fi

cd ..
