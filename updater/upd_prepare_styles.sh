#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

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
    sed "s,mbtiles://{v3},http://localhost/data/v3.json," style.json \
        > style.json.tmp && mv style.json.tmp style.json
    sed "s,{styleJsonFolder}/sprite,http://localhost/styles/${PWD##*/}/sprite," style.json \
        > style.json.tmp && mv style.json.tmp style.json
    sed "s,{fontstack}/{range}.pbf,http://localhost/fonts/{fontstack}/{range}.pbf," style.json \
        > style.json.tmp && mv style.json.tmp style.json
    patch style.json < ../../../updater/osm-bright-gl-style.json.diff
    gzip -kf9 *.json
    cd ..

    cd ..
    echo "styles updated"
else
    echo "styles up to date, skipped"
fi

cd ..
