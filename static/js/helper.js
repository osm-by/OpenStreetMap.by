if (google.loader.ClientLocation){
  geopoint = new L.LatLng(google.loader.ClientLocation.latitude, google.loader.ClientLocation.longitude);
} else {
  geopoint = mmap.getCenter();
}

josm_remote = false;

if (!$.cookie('userid')){
  $.cookie('userid', new Date().getTime()/1000, {expires: 10});
};

$().ready( function(){

  var kosmoUrl = 'https://{s}.tile.openstreetmap.by:3128/osmby-ru/{z}/{x}/{y}.png';

   if (locale == 'en'){
    var kosmoUrl = 'https://{s}.tile.openstreetmap.by:3128/osmby-en/{z}/{x}/{y}.png';
  } else if (locale == 'ru') {
    var kosmoUrl = 'https://{s}.tile.openstreetmap.by:3128/osmby-ru/{z}/{x}/{y}.png';
  } else if (locale == 'be') {
    var kosmoUrl = 'https://{s}.tile.openstreetmap.by:3128/osmby-be/{z}/{x}/{y}.png';
  }// else if (locale == 'none') {
    //var kosmoUrl = 'https://{s}.tile.osmosnimki.ru/kosmo-blank/{z}/{x}/{y}.png';
 // }
  
  mmap.on('click', function(e){
    if (mmap.getZoom()>14){
      map_click(e.lngLat);
    }
  });


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


});
