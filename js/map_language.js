var intl_layers = [
    'water_label',
    'poi_label_4',
    'poi_label_3',
    'poi_label_2',
    'rail_station_label',
    'poi_label_1',
    'airport_label',
    'road_label',
    'place_label_other',
    'place_label_village',
    'place_label_town',
    'place_label_city',
    'marine_label_line_4',
    'marine_label_4',
    'marine_label_line_3',
    'marine_label_point_3',
    'marine_label_line_2',
    'marine_label_point_2',
    'marine_label_line_1',
    'marine_label_point_1',
    'country_label_4',
    'country_label_3',
    'country_label_2',
    'country_label_1'
];

var setMapLanguage = function(map, lang) {
    intl_layers.forEach(function(layer) {
        // name of layer, name of property, value of property
        map.setLayoutProperty(layer, 'text-field', '{name_' + lang + '}');
    });
};