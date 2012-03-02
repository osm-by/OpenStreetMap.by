function OSBmenu(){
  var username = "NoName";
  if ($.cookie("username")){
    username = $.cookie("username");
  };
  $("#osbreport_username").val(username);
  $("#osbreport").dialog('open');
  $("#osbreport_text").focus();
}

function osbResponse(errorMessage) {
  if(errorMessage == undefined){
    $("#osbreport_text").val("");
    $("#osbreport_text").html("");
    $("#osbreport").dialog('close');
  }
  else
    alert("Error creating bug: "+errorMessage);
}

function reportOSB(){
  var text = "";
  text += "";
  text += $("#osbreport_text").val();
  text += " ["+$("#osbreport_username").val() + "@openstreetmap.by]";
  $.cookie("username",$("#osbreport_username").val());
  $.getJSON('http://openstreetbugs.schokokeks.org/api/0.1/addPOIexec?cb=?',{lat: wherenow.lat, lon: wherenow.lng, format: 'js', text: text}, function(data){});
}