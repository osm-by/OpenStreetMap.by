#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset

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
