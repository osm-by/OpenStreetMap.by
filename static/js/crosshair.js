L.Crosshair = L.Class.extend({
	includes: L.Mixin.Events,

	initialize: function() {
	},

	onAdd: function(map) {
		this._map = map;
    //this._container = L.DomUtil.create('div', 'leaflet-crosshair');
		this._canvas = L.DomUtil.create('canvas', 'leaflet-crosshair leaflet-top leaflet-left', this._map._container);//, this._map._panes.markerPane
    //this._map._panes.markerPane.appendChild(this._container);
		map.on('move', this._reset, this);
    //this._map.addLayer(this);
		this._reset();
    
	},

	onRemove: function(map) {
		map._container.removeChild(this._canvas);
		map.off('move', this._reset);
	},
  getPosition: function() {
    return L.Control.Position.TOP_RIGHT;
  },
  getContainer: function() { 
    return this._map._container; 
  },
	_update: function() {
		if (!this._canvas) return;
		var size = this._map.getSize();
		var ctx = this._canvas.getContext("2d");
		this._canvas.width = size.x;
		this._canvas.height = size.y;
		ctx.beginPath();
		ctx.translate(Math.floor(size.x/2)+0.5, Math.floor(size.y/2)+0.5);
		this.draw(ctx);
	},

	_reset: function() {
		var size = this._map.getSize();
		if (this._canvas.width != size.x || this._canvas.height != size.y)
			this._update()
	},

	draw : function(ctx) {
		ctx.moveTo(-10, 0);
		ctx.lineTo(10, 0);
		ctx.moveTo(0, -10);
		ctx.lineTo(0, 10);
		ctx.stroke();
	}
});

