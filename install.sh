#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset


# install dependencies
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    apt-get install gawk bc build-essential python3 python3-venv --no-install-recommends
else
    echo please install manually
fi


# check docker installed
docker info


# create venv
python3 -m venv venv
venv/bin/pip3 install wheel
venv/bin/pip3 install docker-compose
venv/bin/pip3 install shapely

# create tile data
mkdir -p tiledata
