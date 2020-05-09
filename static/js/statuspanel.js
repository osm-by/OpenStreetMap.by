L.Control.StatusPanel = L.Class.extend({
  initialize: function(layer) {
  },

  onAdd: function(map) {
    this._map = map;
    this._container = L.DomUtil.create('div', 'leaflet-control-attribution');

    this._span = L.DomUtil.create('div', null, this._container);
    this._span.innerHTML = "zz";
    this._span.id = "statuspanel";

    var _this = this;
    L.DomEvent.disableClickPropagation(this._container);
  },

  getPosition: function() {
    return L.Control.Position.BOTTOM_RIGHT;
  },

  getContainer: function() {
    return this._container;
  }
});