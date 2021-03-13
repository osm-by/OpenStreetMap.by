# Style

Used [bright style](https://github.com/openmaptiles/osm-bright-gl-style) as default with next modifications:
- removed `water-pattern` style layer.
- added `housenumer` style layer for zooms 15+ (based on [basic style](https://github.com/openmaptiles/maptiler-basic-gl-style) `housenumber` layer) and [expressions](https://docs.mapbox.com/mapbox-gl-js/style-spec/expressions/#interpolate):
     ```
    {
      "id": "housenumber",
      "type": "symbol",
      "source": "openmaptiles",
      "source-layer": "housenumber",
      "minzoom": 15,
      "filter": [
        "==",
        "$type",
        "Point"
      ],
      "layout": {
        "text-field": "{housenumber}",
        "text-font": [
          "Noto Sans Regular"
        ],
        "text-size": [
          "interpolate",
          ["linear"],
          ["zoom"],
          15,
          9,
          17,
          12
        ]
      },
      "paint": {
        "text-color": "rgba(150, 130, 115, 1)",
        "text-opacity": [
          "interpolate",
          ["linear"],
          ["zoom"],
          15,
          0.75,
          17,
          1
        ]
      }
    }
    ```
