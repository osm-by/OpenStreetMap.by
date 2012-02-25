function html_escape(a){
  return (a+"").split("&").join("&amp;").split( "<").join("&lt;").split(">").join("&gt;").split("_").join(" ");
}

function opening_hours_process(oh){
  a = ['Mo','Tu','We','Th','Fr','Sa','Su']
  $.each(a, function(key,val){
    oh = oh.replace(val, _(val));
  })
  oh = oh.replace('off', _('off (weekend)'))
  return oh
}

function map_click(where) {
  $('body').css('cursor', 'wait');
  $.getJSON('?request=click_about',
            {"lat":where.lat, "lon":where.lng, "zoom":mmap.getZoom(), "locale":locale},
            function(data)
    {
      aaa = "<div id='poi-level-tabs'>"; 
      if (!$.isEmptyObject(data.results)){
        levels_available = [];
        for(val in data.results){
          if (data.results.hasOwnProperty(val)){
            val = data.results[val].properties;
            if ((val.level != undefined) && (!(val.level+'' in levels_available)) && (val.level+"" == parseFloat(val.level+""))){
              levels_available.push(val.level+'');
            }
          }
        };
        levels_available.sort(function(a,b){a-b});
        levels_available = $.unique(levels_available);
        levels_available.push('all');
        if (levels_available.length > 1) {
          levels_available.reverse();
          levels_available.sort(function(a,b){a-b});
          
          
          aaa += '<ul>';
          for (level in levels_available) {
            if (levels_available.hasOwnProperty(level)){
              level = levels_available[level];
              aaa += "<li><a href='#level-tabs-"+level+"'>"+ ((level=='all')?_('Other'):level) +_(" floor")+ "</a></li>"
            };
          };
          aaa += '</ul>';
        };
        for (level in levels_available) {
          if (levels_available.hasOwnProperty(level)){
            level = levels_available[level];
            aaa += '<div id="level-tabs-'+level+'" style="max-height:300px; overflow:auto">';
            $.each(data.results, function(key,val){
              val = val.properties;
              if (levels_available.length > 1){
                if ((level != 'all') && (val.level != level) ) return; // TODO: 1-5, 7,8 complicated list parsing
                if ((level == 'all') && (val.level in levels_available) ) return; // TODO: 1-5, 7,8 complicated list parsing
              };
              aaa += "<div>"
              aaa += val.amenity?"<s>"+html_escape(val.amenity)+"</s>":'';
              aaa += val.shop?(val.amenity?", ":"")+"<s>"+html_escape(val.shop)+" shop</s>":'';
              aaa += val.office?((val.shop||val.amenity)?", ":"")+"<s>"+html_escape(val.office)+" office</s>":'';
              aaa += val.craft?((val.shop||val.amenity|val.office)?", ":"")+"<s>"+html_escape(val.craft)+" craft</s>":'';
              //aaa += val.amenity?"<s>"+html_escape(val.amenity)+"</s> ":'';
              aaa += val.name?" <b>"+html_escape(val.name)+"</b>":'';
              aaa += (val.ref && ( (val.name && (val.name.search(val.ref))==-1) || (!val.name) ) )?" <b>"+html_escape(val.ref)+"</b>":'';
              aaa += (val.level && (level == 'all'))?" &nbsp;<i>"+html_escape(val.level)+_(" floor")+"</i>":'';
              aaa += "<br />"
              aaa += val.opening_hours?"<s>Opening hours:</s> "+opening_hours_process(html_escape(val.opening_hours))+"<br>":'';
              aaa += val.atm?"<s>ATM:</s> <s>"+html_escape(val.atm)+"</s><br>":'';
              aaa += val.website?"<s>Web-site:</s> <a href='"+html_escape(val.website)+"'>"+html_escape(val.website)+"</a><br>":'';
              aaa += "<hr /></div>"
            });
            aaa += "</div>";
          };
        };
        if (levels_available.length > 1) aaa += "</div>";
        var popup = new L.Popup({autoPan: false, maxWidth: 600});

        popup.setLatLng(new L.LatLng(data.coords[1], data.coords[0]));
        popup.setContent(aaa);
        
        $('body').css('cursor', 'auto');
        
        mmap.openPopup(popup);
        if (levels_available.length > 1) $('#poi-level-tabs').tabs();
        
        refreshLocales();

      };
    $('body').css('cursor', 'auto');
    })
  return false;

}
 