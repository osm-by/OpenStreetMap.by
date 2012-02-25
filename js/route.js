routelayer = new L.LayerGroup();
routePoints = [];
vehicle='motorcar';
  
  
function updateRoute(){

  mmap.addLayer(routelayer);
  routelayer.clearLayers();
  if (
    vehicle != 'foot' &&
    vehicle != 'bike' &&
    vehicle != 'car'
  ){vehicle = 'car'};
  
  for (var i = 0; i < routePoints.length; i++){
    routePoints[i] = routePoints[i].join(",").split(",");
    routePoints[i] = [parseFloat(routePoints[i][0]).toFixed(6), parseFloat(routePoints[i][1]).toFixed(6)];
  }
  mmap.fire('moveend');
  if (routePoints.length >= 1){
    routelayer.addLayer(new L.Marker(new L.LatLng(routePoints[0][1], routePoints[0][0]),{draggable:true, title:'start'}).on('dragend', function(e){
      routeFrom([e.target.getLatLng().lng,e.target.getLatLng().lat]);
    }));
  }
  if (routePoints.length < 2){
    return false;
  };
  var via = routePoints.join(";");
  
  
  var vehrename = {car:'motorcar', bike:'bicycle', foot:'foot'}
  routelayer.addLayer(new L.Marker(new L.LatLng(routePoints[routePoints.length-1][1], routePoints[routePoints.length-1][0]),{draggable:true, title:'end'}).on('dragend', function(e){
      routeTo([e.target.getLatLng().lng,e.target.getLatLng().lat]);
    }));
  
  $('body').css('cursor', 'wait');
  $.getJSON("http://2.osmosnimki.ru/route/api/dev/?via="+via+"&v="+vehrename[vehicle]+"&fast=1&format=json&callback=?", function(data){
    var lonlats = []
    for (var i=0; i<data.path[0].length; i++){
      lonlats.push(new L.LatLng(data.path[0][i].lat, data.path[0][i].lon));
    }
   // mmap.fitBounds(new L.LatLngBounds(lonlats));
    var color = "blue";
    if (vehicle == "foot") {color = "green"};
    if (vehicle == "bike") {color = "red"};
    var polyline = new L.Polyline(lonlats,{color:color});
    routelayer.addLayer(polyline);
    $('body').css('cursor', 'auto');
  });
   
}

function routeFrom(a){
  if (routePoints.length >= 2){
    routePoints.shift();
  };
  routePoints.unshift(a);
  updateRoute();
}

function routeTo(a){
  if (routePoints.length >= 2){
    routePoints.pop();
  };
  routePoints.push(a);
  updateRoute();
}