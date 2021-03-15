# openstreetmap.by is

1. http://openstreetmap.by web site
2. OSM data with updater
   1. postgres data update based on [`osm2pgsql`](https://github.com/openstreetmap/osm2pgsql) 
   2. vector tiles update based on [`openmaptiles`](https://github.com/openmaptiles/openmaptiles)

# Hardware

Since 2020 OpenStreetMap.by runs on 64Gb RAM and 2x512 SSD server
at https://www.hetzner.com and costs @Komzpa 40.80 EUR monthly.

![OpenStreetMap.by Hardware](docs/server.jpg)

# Software

## Initialize project
 
 1. clone repo `git clone https://github.com/osm-by/OpenStreetMap.by.git`
 2. init submodules `git submodule update --init --recursive` that initialize `openmaptiles`   
 3. run [`install.sh`](install.sh) - make sure that you have all required packages
 4. run [`updater/update.sh`](updater/update.sh) - fetch and prepare data:
    1. download latest osm dump for belarus
    2. update postgis database with `osm2pgsql`
    3. generate mbtiles for Belarus 0-14 zoom levels
    4. generate overview mbtiles for planet 0-4 zoom levels
    5. unpack mbtiles to filesystem to allow serve it by nginx.
    6. download, patch and prepare vector tiles styles
    7. download and prepare vector tiles fonts
    8. download and prepare vector tiles data info
 5. check that [`.env`](.env) contains good for your configuration 
 6. run `docker-compose up -d nginx` run `nginx` and all required services locally.


## Schema of openstreetmap.by work

                     nginx
                       |
      --------------------------
      |         |              |
    static---webapp       (tileserver)
                |              |
            ----------         |
            |        |         |
          redis   postgis   tiledata
                     |         |
    =================+=========+=========
                     |         |
                   updater-belarus


*NOTE: tileserver can be replaced with serving tile data as standard static data serving by nginx.*

`redis` store only untranslated text keys.

`postgis` provide `osm2pgsql` schema and used for read only purpose.

See details in [`docker-compose.yml`](docker-compose.yml).


## Schema of tiledata directory

- `belarus-latest.osm.pbf` - osm dump
- `belarus.mbtiles` - mbtiles generated for Belarus osm dump zooms 0-14
- `planet.mbtiles` - mbtiles generated for planet overview zooms 0-4
- `belarus/` - vector tiles for Belarus osm dump zooms 0-14 unpacked from `belarus.mbtiles`
- `planet/` - vector tiles for planet overview zooms 0-4 unpacked from `planet.mbtiles`
- `data/` - vector tile data info
- `styles/` - styles for vector tiles rendering
- `fonts/` - fonts used by styles for vector tiles rendering

`tiledata` directory fully populated with [`updater/update.sh`](updater/update.sh) script.

Most of this data server by `nginx`, see details in [`nginx/openstreetmap.by.conf`](nginx/openstreetmap.by.conf).


## Styles

Used [bright style](https://github.com/openmaptiles/osm-bright-gl-style) as default with next modifications:
- removed `water-pattern` style layer.
- added `housenumer` style layer for zooms 15+ (based on [basic style](https://github.com/openmaptiles/maptiler-basic-gl-style) `housenumber` layer) and [expressions](https://docs.mapbox.com/mapbox-gl-js/style-spec/expressions/#interpolate).

As part of the styles used appropriate [fonts](https://github.com/openmaptiles/fonts/).


## Generate and view vector tiles from scratch  

### mbtiles generation

See https://github.com/osm-by/openmaptiles (slightly modified fork of https://github.com/openmaptiles/openmaptiles).

    git clone https://github.com/osm-by/openmaptiles.git
    cd openmaptiles
    python3 -m venv venv
    . venv/bin/activate
    pip install docker-compose
    ./quickstart.sh belarus

### tileserver run

See https://github.com/maptiler/tileserver-gl.

    docker run --rm -it -v $(pwd)/data:/data -p 8081:80 maptiler/tileserver-gl
