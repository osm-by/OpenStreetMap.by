
L.Control.Embed = L.Class.extend({
  onAdd: function(map) {
    this._map = map;
    this._container = L.DomUtil.create('div', 'leaflet-control-zoom');
    
    this._EmbedButton = this._createButton(
        'Embed', 'leaflet-control-embed-button', this._embedDialog, this);
    this._container.appendChild(this._EmbedButton);
    this._dialog = $('#embeddialog')
    .dialog({
      autoOpen: false,
      title: _('Embeddable map'),
      width: 600,
      modal: true
    })
    $('#embed_crosshair').change(redrawEmbed);
    $('#embed_lang').change(redrawEmbed);
    $('#embed_marker').change(redrawEmbed);
    $('#embed_marker_label').change(redrawEmbed);
    $('#embed_marker_label').keyup(redrawEmbed);


  },
  
  getContainer: function() { 
    return this._container; 
  },
  
  getPosition: function() {
    return L.Control.Position.TOP_RIGHT;
  },
  _embedDialog: function(){
    redrawEmbed();
    this._dialog.dialog('open');
  },
  _createButton: function(title, className, fn, context) {
    var link = document.createElement('a');
    link.href = '#';
    link.title = title;
    link.className = className;

    L.DomEvent.disableClickPropagation(link);
    L.DomEvent.addListener(link, 'click', L.DomEvent.preventDefault);
    L.DomEvent.addListener(link, 'click', fn, context);
    
    return link;
  }
});

function redrawEmbed(){
  $("#embed_marker:checked").val()?$('#embed_marker_label_div').show():$('#embed_marker_label_div').hide();
  $('#embedtext').html('<iframe width="425" height="350" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" src="https://openstreetmap.by/embed'+
  '?lat=' + mmap.getCenter().lat +
  '&amp;lon=' + mmap.getCenter().lng +
  '&amp;zoom=' + mmap.getZoom() + 
  ($("#embed_crosshair:checked").val()?('&amp;crosshair=true'):'') +
  ($("#embed_marker:checked").val()?
     ("&amp;marker=true" + ($("#embed_marker_label").val()?"&amp;markertext="+encodeURIComponent($("#embed_marker_label").val()):"") )
     :'') + 
  '&amp;lang=' + $("#embed_lang").val()+
  
  '" style="border: 1px solid black"></iframe>');  
}
