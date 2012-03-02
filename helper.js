


josm_remote = false;

$.getJSON('http://localhost:8111/version?jsonp=?', function(data){josm_remote = data;});

$().ready( function(){

  mmap.attributionControl.setPrefix("");
  
  
  var kosmoUrl = 'http://{s}.tile.osmosnimki.ru/kosmo-be/{z}/{x}/{y}.png';
  if (locale == 'ru'){var kosmoUrl = 'http://{s}.tile.osmosnimki.ru/kosmo/{z}/{x}/{y}.png';  }
  if (locale == 'en'){var kosmoUrl = 'http://{s}.tile.osmosnimki.ru/kosmo-en/{z}/{x}/{y}.png';}
  
  kosmo = new L.TileLayer(kosmoUrl, {maxZoom: 18, attribution: _("Map data © <a href='http://osm.org'>OpenStreetMap</a> contributors, CC-BY-SA; rendering by <a href='http://kosmosnimki.ru'>kosmosnimki.ru</a>")});
  mmap.addControl(new L.Control.Breadcrumbs());
  mmap.addLayer(kosmo);
  
  mmap.addControl(new L.Control.Dirty(kosmo));
  
  mmap.on('click', function(e){
      if (mmap.getZoom()>14){
        map_click(e.latlng);
      }
    })
  
  mmap.addControl(new L.Control.Embed());
  
  

$("#osbreport").dialog(
  {
    autoOpen: false,
    title: _('Report a problem on map'),
    width: 750,
    height: 480,
    modal: true
  }
);
$("#osbreport_send").click(reportOSB);



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
$("#map").contextMenu( context_menu );


updateRoute();
//mmap.addControl(new L.Crosshair());


});