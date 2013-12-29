if (google.loader.ClientLocation){
  geopoint = new L.LatLng(google.loader.ClientLocation.latitude, google.loader.ClientLocation.longitude);
} else {
  geopoint = mmap.getCenter();
}

josm_remote = false;

if (!$.cookie('userid')){
  $.cookie('userid', new Date().getTime()/1000, {expires: 10});
};

$.getJSON('http://localhost:8111/version?jsonp=?', function(data){josm_remote = data;});

$().ready( function(){

  mmap.attributionControl.setPrefix("");
  
  
  var kosmoUrl = 'http://{s}.tile.openstreetmap.by:3128/osmby-ru/{z}/{x}/{y}.png';
/*  
   if (locale == 'en'){
    var kosmoUrl = 'http://{s}.tile.openstreetmap.by:3128/osmby-en/{z}/{x}/{y}.png';
  } else if (locale == 'ru') {
    var kosmoUrl = 'http://{s}.tile.openstreetmap.by:3128/osmby-ru/{z}/{x}/{y}.png';
  } else if (locale == 'be') {
    var kosmoUrl = 'http://{s}.tile.openstreetmap.by:3128/osmby-be/{z}/{x}/{y}.png';
  }// else if (locale == 'none') {
    //var kosmoUrl = 'http://{s}.tile.osmosnimki.ru/kosmo-blank/{z}/{x}/{y}.png';
 // }
*/
  kosmo = new L.TileLayer(kosmoUrl, {maxZoom: 18, attribution: _("Map data © <a href='http://osm.org'>OpenStreetMap</a> contributors")});
  //mmap.addControl(new L.Control.Breadcrumbs());
  
  mmap.addLayer(kosmo);
  
  //mmap.addControl(new L.Control.Dirty(kosmo));
  //mmap.addControl(new L.Control.StatusPanel());
  
  mmap.on('click', function(e){
      if (mmap.getZoom()>14){
        map_click(e.latlng);
      }
    })
  //mmap.addControl(new L.Control.Embed());


$("#downloadmaps").dialog(
  {
      autoOpen: false,
      title: _('Download OpenStreetMap'),
      width: 750,
      height: 480,
      modal: true
    }).tabs({
   load: function(event, ui) { refreshLocales(); }
});

$("#downloadlink").show().click(function(){
  $("#downloadmaps").dialog('open');
  return false;
})

$.contextMenu.theme = 'osx';
$(".leaflet-map-pane").contextMenu( context_menu );


mmap.on('locationfound', function(e){
  geopoint = e.latlng;
})

mmap.locate({'watch':true, 'enableHighAccuracy': true, 'maximumAge': 30})

});