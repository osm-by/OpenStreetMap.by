    function search() {
      $('body').css('cursor', 'wait');
      $.getJSON('?request=geocode',
                {"lat":mmap.getCenter().lat, "lon":mmap.getCenter().lng, "zoom":mmap.getZoom(), "text": $('#searchbox').val()},
                function(data)
        {
        var aaa = "";
        if (!$.isEmptyObject(data.results)){
          data.results = [data.results[0]];
          $.each(data.results, function(key,val)
            {
                box = [99999,9999,-9999,-99999];
                $.each(val["coordinates"][0], function(key,val){
                  box = [Math.min(box[0],val[0]),Math.min(box[1],val[1]),Math.max(box[2],val[0]),Math.max(box[3],val[1])];
                });
                mmap.fitBounds(new L.LatLngBounds(new L.LatLng(box[1],box[0]),new L.LatLng(box[3],box[2])));
                
            });
        }
        $('body').css('cursor', 'auto');
        var legend = document.getElementById("leaflet-control-breadcrumbs");
        

        })
     return false;
    
  }
 