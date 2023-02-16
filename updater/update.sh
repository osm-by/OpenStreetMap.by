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


docker-compose run --rm management bash updater/upd_prepare_styles.sh
docker-compose run --rm management bash updater/upd_prepare_fonts.sh

if [ $1 = "all" ] || [ $1 = "belarus" ]; then
  docker-compose run --rm management bash updater/upd_download_belarus_dump.sh
  docker-compose run --rm management bash updater/upd_update_postgis.sh
  bash updater/upd_generate_belarus_mbtiles.sh
  docker-compose run --rm management bash updater/upd_unpack_belarus_mbtiles.sh
fi

if [ $1 = "all" ] || [ $1 = "planet" ]; then
  docker-compose run --rm management bash updater/upd_download_planet_dump.sh
  bash updater/upd_generate_planet_mbtiles.sh
  docker-compose run --rm management bash updater/upd_unpack_planet_mbtiles.sh
fi

docker-compose run --rm management bash updater/upd_prepare_tile_data_info.sh

rm -f openmaptiles/data/belarus.osm.pbf
rm -f openmaptiles/data/belarus.bbox
rm -f openmaptiles/data/planet.osm.pbf
rm -f openmaptiles/data/planet.bbox
rm -f tiledata/planet-latest.osm.pbf
rm -f tiledata/planet.mbtiles
