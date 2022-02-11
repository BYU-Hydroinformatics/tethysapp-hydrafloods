// Get a cookie
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// find if method is csrf safe
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

// add csrf token to appropriate ajax requests
$(function() {
    var input_spatial ="";
    //Start Map //
    var map = L.map('map').setView([8.913648, -79.544706], 10);

    var water_layer = L.tileLayer('',{attribution:
          '<a href="https://earthengine.google.com" target="_">' +
          'Google Earth Engine</a>;'}).addTo(map).bringToFront();

    var image_layer = L.tileLayer('',{attribution:
          '<a href="https://earthengine.google.com" target="_">' +
          'Google Earth Engine</a>;'}).addTo(map);

    // var baseMaps = creationMaps();
    // console.log(baseMaps)
    // L.esri.Vector.vectorBasemapLayer('ArcGIS:Navigation', {
    //     apikey: "AAPK052bec1846714415aed2c85ddfa15f73KYexWiKoe0Au2nFQprFm_CWnafrYs4Y3MwTI3iqb-QBEwR808TRyXrudF4Za40V-" // Replace with your API key - https://developers.arcgis.com
    // }).addTo(map);

    var positron = L.tileLayer('http://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png', {
          attribution: '©OpenStreetMap, ©CartoDB'
        }).addTo(map);

    var baseMaps = {"Basemap":positron}
    var varMaps = {"Satellite Observation":image_layer,"Water":water_layer,}

    L.control.layers(baseMaps,varMaps,{position: 'bottomleft'}).addTo(map);

     // FeatureGroup is to store editable layers
     drawnItems = new L.FeatureGroup().addTo(map);   // FeatureGroup is to store editable layers

     let drawControl = new L.Control.Draw({
       edit: {
         featureGroup: drawnItems,
         edit: true,
       },
       draw: {
         marker: true,
         polyline: false,
         circlemarker: false,
         circle: false,
         polygon: true,
         rectangle: true,
         trash: true,
       },
     });
     map.addControl(drawControl);

     // getting dataset from bottons
     if($("#landsat8") == 'on') {
         satelite = 'landsat8'
     } else {
         satelite = 'sentinel1'
     }
     
     $("#load_data").click(function(){
         let dataset = satelite;
         let end_date = $('#end_date').val();
         let start_date = $('#start_date').val();
         let terrain =  $("#terrain_correction_id").val();
         let speckle =  $("#speckle_filter_id").val();
         let cloud = $("#cloud_mask_id").val();
 
         var request_obj={
             'input_spatial':input_spatial,
             'dataset' : dataset,
             'start_date': start_date,
             'end_date': end_date,
             'terrain': terrain,
             'speckle': speckle,
             'cloud': cloud
         }
         console.log(request_obj);
         $("#GeneralLoading").removeClass("hidden");
         $.ajax({
             type:"GET",
             url:'get-image-layer/',
             datatype:"JSON",
             data:request_obj,
             success: function(data){
                 $("#GeneralLoading").addClass("hidden");
                 console.log(data)
                 water_layer.setUrl(data.water_url)
                 image_layer.setUrl(data.image_url)
                 // you need to make a pop up appear
                 //1 create the pop in th html, your popup should have a button called close
                 //2 make it appear $("#id").show();
                
             },
             error: function(error){
                 console.log(error)
                 $("#GeneralLoading").addClass("hidden");
                  // you need to make a pop up appear
                 //1 create the pop in th html, your popup should have a button called close
                 //2 make it appear $("#id").show();
             }
         })
     })
     map.on(L.Draw.Event.CREATED, function (e) {
            // console.log('Draw Event Created');
            drawnItems.addLayer(e.layer);
            input_spatial = JSON.stringify(e.layer.toGeoJSON());
            // type_of_series = e.layerType;
      });

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
        }
    });
}); //document ready;
