L.Control.Breadcrumbs = L.Class.extend({
  onAdd: function(map) {
    this._container = L.DomUtil.create('div', 'leaflet-control-breadcrumbs');
    this._map = map;
    this._json_in_progress=false;
    this._update();
    this._map.on('moveend', this._update, this);
  },

  getPosition: function() {
    return L.Control.Position.TOP_LEFT;
  },

  getContainer: function() {
    return this._container;
  },

  _update: function() {
    if (!this._map) return;
    if (this._json_in_progress){clearTimeout(this._json_in_progress);};
    this._json_in_progress = setTimeout( (function(ctx) { return function(){
      
      $.getJSON('?request=describe',
                {"lat":mmap.getCenter().lat, "lon":mmap.getCenter().lng, "zoom":mmap.getZoom(), "locale": locale},
                function(data)
        {
        var aaa = "";
        $.each(data.breadcrumbs, function(key,val)
          {
              box = [99999,9999,-9999,-99999];
              $.each(val[2]["coordinates"][0], function(key,val){
                box = [Math.min(box[0],val[0]),Math.min(box[1],val[1]),Math.max(box[2],val[0]),Math.max(box[3],val[1])];
              });
              aaa += " » <span onclick='mmap.fitBounds(new L.LatLngBounds(new L.LatLng("+box[1]+","+box[0]+"),new L.LatLng("+box[3]+","+box[2]+")));' class='breadcrumbs' title='"+val[0]+"' >" + val[1] + "</span><wbr> ";
          });
        var legend = document.getElementById("leaflet-control-breadcrumbs");
        ctx._container.innerHTML = aaa;
        ctx._json_in_progress = false;
        })
    }}(this)),300);
  }
});