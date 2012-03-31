routelayer = new L.LayerGroup();
routePoints = [];
vehicle='car';
currentRoute = {};
  
  
function updateRoute(){

  mmap.addLayer(routelayer);
  routelayer.clearLayers();
  if (
    vehicle != 'foot' &&
    vehicle != 'bike' &&
    vehicle != 'car'  &&
    vehicle != 'taxi' 
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
  
  
  var vehrename = {car:'motorcar', bike:'bicycle', foot:'foot', taxi:'car'}
  routelayer.addLayer(new L.Marker(new L.LatLng(routePoints[routePoints.length-1][1], routePoints[routePoints.length-1][0]),{draggable:true, title:'end'}).on('dragend', function(e){
      routeTo([e.target.getLatLng().lng,e.target.getLatLng().lat]);
    }));
  
  $('body').css('cursor', 'wait');
  $.getJSON("http://2.osmosnimki.ru/route/api/dev/?via="+via+"&v="+vehrename[vehicle]+"&fast=1&format=json&callback=?", function(data){
    currentRoute = data;
    var lonlats = []
    for (var i=0; i<data.path[0].length; i++){
      lonlats.push(new L.LatLng(data.path[0][i].lat, data.path[0][i].lon));
    }
   // mmap.fitBounds(new L.LatLngBounds(lonlats));
    var color = "blue";
    if (vehicle == "foot") {color = "green"};
    if (vehicle == "bike") {color = "red"};
    if (vehicle == "taxi") {color = "magenta"};
    var polyline = new L.Polyline(lonlats,{color:color});
    routelayer.addLayer(polyline);
    if (data.distance>0){
      var prettydistance = ((Math.floor(data.distance)>0)?(Math.floor(data.distance) + _(" km")):'') +" ";
          prettydistance + (Math.floor((Math.floor(data.distance*1000))-1000*Math.floor(data.distance))>0) ? 
                          (Math.floor((Math.floor(data.distance*1000))-1000*Math.floor(data.distance)) + _("m")): _("exactly");
      var roundedtime = Math.ceil(data.time/60/2)*2, // rounding up to 2 minutes
          prettytime = ((roundedtime>=60)?Math.floor(roundedtime/60)+":":'');
          prettytime += ((((roundedtime>=60) && (roundedtime % 60)<10))?"0":'')+ (roundedtime % 60) + ((roundedtime<60)?' '+ _("min"):'');
      
      $("#statuspanel").html(
        "<b>"+_("Route length:")+"</b> "+prettydistance+"<br />"+
        ((vehicle=='car' || vehicle == 'taxi')?("<b>"+_("Travel time:")+"</b> "+prettytime+"<br />"):'')
      );
      
      if (vehicle == "taxi" && canRouteTaxi()){
        $.getJSON("http://taxi.andreylis.belinfonet.by/osmAPI?callback=?", {time: data.time/60, distance:data.distance}, function(data){
          var b = "<table><tr><td><b>"+_("Service Phone")+"</b></td><td><b>"+_("Price (est.)")+"</b></td></tr>";
          for (i in data){
            b += "<tr><td align='center'>"+i+"</td><td align='right'>"+(Math.floor(Math.ceil(data[i]/1000)*1000)).toString().replace(/(\d)(?=(\d\d\d)+(?!\d))/g, "$1 ") + _(" BYR")+"</td></tr>";
          }
          b += "</table>";
          
          $("#statuspanel").html(
          b+$("#statuspanel").html()
          )
        })
      }
    } else
    {
      $("#statuspanel").html("");
    }
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

function canRouteTaxi(){
  var rp = routePoints;
  for (var i = 0; i < rp.length; i++){
    if (!((rp[i][0]>27.3699984458077) && (rp[i][0]<28.0895335373645) && (rp[i][1]>53.7928745722116) && (rp[i][1] < 53.9742910534496))){
      return false;
    }
  }
  return true;
}