# Overview of openstreetmap.by project work

Project contains 2 major parts:
1. http://openstreetmap.by web part
2. data updater
   1. postgres data update based on [`osm2pgsql`](https://github.com/openstreetmap/osm2pgsql) 
   2. vector tiles update based on [`openmaptiles`](https://github.com/openmaptiles/openmaptiles)


## Initialize project
 
 1. run `install.sh` - make sure that you have all required packages, initialize `openmaptiles`
 2. run `updater/update.sh` - fetch and prepare data:
    1. download latest osm dump for belarus
    2. update postgis database with `osm2pgsql`
    3. generate mbtiles for Belarus 0-14 zoom levels
    4. generate overview mbtiles for planet 0-4 zoom levels
    5. unpask mbtiles to filesystem to allow serve it by nginx.
    6. download and prepare vector tiles styles
    7. download and prepare vector tiles fonts
    8. download and prepare vector tiles data info
 3. check that `.env` contains good for your cofiguration 
 4. run `docker-compose up -d nginx` run `nginx` and all required services locally.


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

See details in `docker-compose.file`.


## Schema of tiledata directory

- `belarus-latest.osm.pbf` - osm dump
- `belarus.mbtiles` - mbtiles generated for Belarus osm dump zooms 0-14
- `planet.mbtiles` - mbtiles generated for planet overview zooms 0-4
- `belarus/` - vector tiles for Belarus osm dump zooms 0-14 unpacked from `belarus.mbtiles`
- `planet/` - vector tiles for planet overview zooms 0-4 unpacked from `belarus.mbtiles`
- `data/` - vector tile data info
- `styles/` - styles for vector tiles rendering
- `fonts/` - fonts used by styles for vector tiles rendering

`tiledata` directory fully populated with `updater/update.sh` script.

Most of this data server by `nginx`, see details in `nginx.conf`.


## Generate and view vector tiles from scratch  

### mbtiles generation

See https://github.com/openmaptiles/openmaptiles.

    git clone https://github.com/openmaptiles/openmaptiles/archive/master.zip
    cd openmaptiles
    python3 -m venv venv
    . venv/bin/activate
    pip install docker-compose
    patch < updater/openmaptiles.patch  # optional
    ./quickstart.sh belarus

### tileserver run

See https://github.com/maptiler/tileserver-gl.

    docker run --rm -it -v $(pwd)/data:/data -p 8081:80 maptiler/tileserver-gl
