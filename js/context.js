  function round_point (point) {
    var bounds = mmap.getBounds(), size = mmap.getSize();
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
  };



function context_menu(e){
  
  wherenow = round_point(mmap.mouseEventToLatLng(e));
  
  var menu = [];
  var item = {};
  item[ wherenow.lat+', '+wherenow.lng] = {onclick:function(menuItemClicked,menuObject) { mmap.panTo(wherenow); }};
  menu.push(item);
  menu.push( $.contextMenu.separator);
  
  if (routePoints.length < 1) {
      var item = {};
      item[ _("Route to here")] = {onclick:function(menuItemClicked,menuObject) { routeTo([wherenow.lng, wherenow.lat]); routeFrom([0,0]) }};
      menu.push(item);
  }
  
  if (routePoints.length >= 1) {

      var item = {};
      item[ _("Route from here")] = {onclick:function(menuItemClicked,menuObject) {from_geolocation = false; routeFrom([wherenow.lng, wherenow.lat]) }};
      menu.push(item);
      
      var item = {};
      item[ _("Route to here")] = {onclick:function(menuItemClicked,menuObject) { routeTo([wherenow.lng, wherenow.lat]) }};
      menu.push(item);
    
      var item = {};
      item[(vehicle!="bike"?'☐ ':'☑ ')+ _("Route as bicycle")] = {onclick:function(menuItemClicked,menuObject) { vehicle="bike"; updateRoute(); }, icon:"/img/bicycle_16.png", disabled: vehicle=="bike"};
      menu.push(item);

      var item = {};
      item[(vehicle!="car"?'☐ ':'☑ ')+ _("Route as car")] = {onclick:function(menuItemClicked,menuObject) { vehicle="car"; updateRoute(); }, icon:"/img/wheel_16.png", disabled: vehicle=="car"};
      menu.push(item);
      if (canRouteTaxi()){
        var item = {};
        item[(vehicle!="taxi"?'☐ ':'☑ ')+ _("Route as taxi")] = {onclick:function(menuItemClicked,menuObject) { vehicle="taxi"; updateRoute(); }, icon:"/img/taxi_c.png", disabled: vehicle=="taxi"};
        menu.push(item);
      }
      var item = {};
      item[ _("Reverse route")] = {onclick:function(menuItemClicked,menuObject) { routePoints.reverse(); updateRoute(); }, icon:"/img/reverse.png"};
      menu.push(item);
      
      var item = {};
      item[ _("Clear route")] = {onclick:function(menuItemClicked,menuObject) {from_geolocation = true; routePoints = []; updateRoute(); }, icon:"/img/delete_icon.gif"};
      menu.push(item);
  }
  
  menu.push( $.contextMenu.separator);
  
  var item = {};
  item[ (_("Report a problem") + ((mmap.getZoom()<13)?(" ("+ _("please zoom in")+")"):''))] = {onclick:OSBmenu, icon:"/img/osb_icon.png", disabled: mmap.getZoom()<13};
  menu.push(item);
  
  
  
  
  if (josm_remote){
    var item = {};
    item[_("Edit via ")+josm_remote.application ] = {
      onclick:function(menuItemClicked,menuObject) { $.getJSON('http://localhost:8111/load_and_zoom?left='+(wherenow.lng-0.001)+'&right='+(wherenow.lng+0.001)+'&top='+(wherenow.lat+0.0005)+'&bottom='+(wherenow.lat-0.0005)+'&jsonp=?', function(data){}); },
      icon: '/img/icon_to_josm.png'
    }
    menu.push(item);
  }else{
    var item = {};
    item[_("Edit on OpenStreetMap.org")] = function(menuItemClicked,menuObject) { window.open('http://openstreetmap.org/edit?lon='+wherenow.lng+'&lat='+wherenow.lat+'&zoom='+mmap.getZoom(),"_blank")};
    menu.push(item);
  };
  return menu
  
  
}