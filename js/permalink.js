L.Control.Permalink = L.Control.extend({
      includes: L.Mixin.Events, 

        options: {
                position: "bottomleft",
                useAnchor: true,
                useLocation: false,
                text: "Permalink"
        },

  initialize: function() {
    this._set_urlvars();
    this._centered = false;
  },

  onAdd: function(map) {
    map.on('moveend', this._update, this);
    this._map = map;
    this._container = L.DomUtil.create('div', 'leaflet-control-attribution');
    /*
    this._container = L.DomUtil.create('div', 'leaflet-control-attribution');
    L.DomEvent.disableClickPropagation(this._container);
    
    
    this._href = L.DomUtil.create('a', null, this._container);
    this._href.innerHTML = "Permalink";
    
    */
    this._set_center(this._params);
    this._update();
    if ("q" in this._params){
      $('#searchbox').val(this._params.q);
      search();
    }
    if ("lang" in this._params){
      if (this._params.lang in ['en', 'be', 'ru']){
        locale = this._params.lang || locale || "be";
      }
      else{
        locale = $.cookie("lang") || "en";
      }
    }
  },

  getPosition: function() {
    return L.Control.Position.BOTTOM_RIGHT;
  },

  getContainer: function() {
    return this._container;
  },

  _update: function() {
    if (!this._map) return;

    var center = this._map.getCenter();
    center = this._round_point(center);
    this._params['zoom'] = this._map.getZoom();
    this._params['lat'] = center.lat;
    this._params['lon'] = center.lng;
    delete this._params['via'];
    delete this._params['vehicle'];
    delete this._params['lang'];
    if (routePoints.length > 1){
      this._params['via'] = routePoints.join(";");
      this._params['vehicle'] = vehicle;
    }


    var url = [];
    for (var i in this._params) {
      if (this._params.hasOwnProperty(i)){
        url.push(i + "=" + this._params[i]);
        $.cookie(i, this._params[i], {expires:7});
      }
    }
    $.cookie("lang", locale, {expires:7});

    //this._href.setAttribute('href', this._url_base + "?" + url.join('&'));
    if (history.replaceState) {      history.replaceState({},"",this._url_base + "?" + url.join('&'));    };
  },

  _round_point : function(point) {
    var bounds = this._map.getBounds(), size = this._map.getSize();
    var ne = bounds.getNorthEast(), sw = bounds.getSouthWest();

    var round = function (x, p) {
      if (p == 0) return x;
      shift = 1;
      while (p < 1 && p > -1) {
        x *= 10;
        p *= 10;
        shift *= 10;
      }
      return Math.floor(x)/shift;
    }
    point.lat = round(point.lat, (ne.lat - sw.lat) / size.y);
    point.lng = round(point.lng, (ne.lng - sw.lng) / size.x);
    return point;
  },

  _set_urlvars: function()
  {
    this._params = {};
    var idx = window.location.href.indexOf('?');
    if (idx < 0) {
      this._url_base = window.location.href;
      return;
    }
    var params = window.location.href.slice(idx + 1).split('&');
    for(var i = 0; i < params.length; i++) {
      var tmp = decodeURIComponent((params[i] + '').replace(/\+/g, '%20')).split('=');
      this._params[tmp[0]] = tmp[1];
    }
    this._url_base = window.location.href.substring(0, idx);
  }, 

  _set_center: function(params)
  {
    if (params.via != undefined) {
      routePoints = [];
      var i = params.via.split(";");
      from_geolocation = false;
      for (j = 0; j < i.length; j++) {
        var k =[parseFloat(i[j].split(",")[0]), parseFloat(i[j].split(",")[1])];
        if ((k[0] ==0 )&&(k[1]==0)){
          from_geolocation = true;
        }
        routePoints.push(k);
      };
      
    }

    vehicle = params.vehicle || $.cookie('vehicle');
    locale = params.lang || $.cookie('lang');

    if (this._centered) return;
    

    if ((params.zoom == undefined) && ($.cookie('zoom')!= undefined)) { params.zoom = $.cookie('zoom')};
    if ((params.lat  == undefined) && ($.cookie('lat') != undefined)) { params.lat = $.cookie('lat') };
    if ((params.lon  == undefined) && ($.cookie('lon') != undefined)) { params.lon = $.cookie('lon') };
    if ((params.lat == NaN) || (params.lon == NaN) || (params.zoom == NaN)) {params.lon = 0; params.lat=0; params.zoom=2}
    if (params.zoom == undefined ||
        params.lat == undefined ||
        params.lon == undefined) return;
    
    this._centered = true;

    this._map.setView(new L.LatLng(params.lat, params.lon), params.zoom);
  }
});