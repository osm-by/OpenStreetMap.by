#!/bin/bash
set -x


# install dependencies
sudo apt-get install wget unzip patch gawk docker-compose build-essential python3 python3-venv postgresql-client osm2pgsql


# check docker installed
docker info


# install openmaptiles
wget https://github.com/openmaptiles/openmaptiles/archive/master.zip
unzip -o *.zip
rm -f *.zip
mv openmaptiles-* openmaptiles
cd openmaptiles
patch < ../updater/openmaptiles.patch
cd ..


# create venv
python3 -m venv venv


# create tile data
mkdir -p tiledata
