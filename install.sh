#!/bin/bash
set -o errexit
set -o pipefail
set -o nounset


# install dependencies
apt-get install wget unzip patch gawk bc build-essential python3 python3-venv postgresql-client osm2pgsql --no-install-recommends


# check docker installed
docker info


# create venv
python3 -m venv venv
venv/bin/pip3 install wheel
venv/bin/pip3 install docker-compose

# create tile data
mkdir -p tiledata
