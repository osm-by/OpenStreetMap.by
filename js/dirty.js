L.Control.Dirty = L.Class.extend({
  initialize: function(layer) {
    this._layer = layer;
    this._frames = {};
    this._count_sched = this._count_load = 0;
  },

  onAdd: function(map) {
    this._map = map;
    this._container = L.DomUtil.create('div', 'leaflet-control-attribution');

    this._span = L.DomUtil.create('div', null, this._container);
    this._span.innerHTML = "Invalidate";

    var _this = this;
    L.DomEvent.disableClickPropagation(this._container);
    L.DomEvent.addListener(this._container, 'click',
      function() { _this._invalidate(); });
  },

  getPosition: function() {
    return L.Control.Position.BOTTOM_LEFT;
  },

  getContainer: function() {
    return this._container;
  },

  _invalidate: function(x)
  {
    for(var i in this._layer._tiles) {
      var frame = this._createFrame(i);
      frame.src = this._layer._tiles[i].src + '/dirty';
      this._frames[i] = frame;
      this._container.appendChild(frame);
      this._count_sched += 1;
    }
    this._update_label();
  },

  _createFrame: function(id) {
    var _this = this;
    var frame = L.DomUtil.create('iframe', 'leaflet-frame');
    frame.style.width = frame.style.height = "0px";
    frame.id = id
    frame.onload = function() { _this._frameLoaded(id) };
    return frame;
  },

  _frameLoaded: function(id) {
    this._container.removeChild(this._frames[id]);
    delete this._frames[id];
    this._count_load += 1;
    this._update_label();
    if (this._count_load == this._count_sched) {
      this._layer._reset(true);
      this._layer._update();
    }
  },

  _update_label: function() {
    this._span.innerHTML = "Invalidate " + this._count_load + "/" + this._count_sched;
  }
});