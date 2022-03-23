var water_layer;
var image_layer;
var map;
var controlL;

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

// Add method to layer control class
L.Control.Layers.include({
    getOverlays: function() {
      // create hash to hold all layers
      var control, layers;
      layers = {};
      control = this;
  
      // loop thru all layers in control
      control._layers.forEach(function(obj) {
        var layerName;
  
        // check if layer is an overlay
        if (obj.overlay) {
          // get name of overlay
          layerName = obj.name;
          // store whether it's present on the map or not
          return layers[layerName] = control._map.hasLayer(obj.layer);
        }
      });
  
      return layers;
    }
  });

// add csrf token to appropriate ajax requests
$(function() {
    var satellite = "sentinel1";
    var input_spatial ="";
    var terr_val = 'yes';
    var spec_val = 'yes';
    var cloud_val = 'yes';
    var flood_val = 'no';
    var water_period = '1';
    var occurance_thresh = '75';


    //Start Map //
    map = L.map('map').setView([20, -40], 3);

    water_layer = L.tileLayer('',{attribution:
          '<a href="https://earthengine.google.com" target="_">' +
          'Google Earth Engine</a>;'}).addTo(map).bringToFront();

    flood_layer = L.tileLayer('',{attribution:
    '<a href="https://earthengine.google.com" target="_">' +
    'Google Earth Engine</a>;'}).addTo(map);

    image_layer = L.tileLayer('',{attribution:
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
    var varMaps = {"Satellite Observation":image_layer,"Water":water_layer, "Flood": flood_layer}

    controlL = L.control.layers(baseMaps,varMaps,{position: 'bottomleft'})
    controlL.addTo(map);

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

     // set initial ui to have sentinel1 button active
     // and cloud mask opt hidden
     $("#sentinel1").addClass('active');
     $("#cloud_mask_p").hide();
     $("#cloud_mask_id").hide();
     $("#cloud_mask_id").hide();
     $("#water_period_id").hide(); 
     $("#water_period_p").hide();

     function check_flood(water_period, flood_val){
        if(flood_val == 'yes'){
            $("#water_period_id").show(); 
            $("#water_period_p").show();
            if (water_period == '1'){
                $("#occurance_thresh_id").addClass('hidden');
                $("#occurance_thresh_p").addClass('hidden');
            }
            else {
                $("#occurance_thresh_id").removeClass('hidden');
                $("#occurance_thresh_p").removeClass('hidden');
            }
        } 
        else {
            $("#water_period_id").hide(); 
            $("#water_period_p").hide();
            $("#occurance_thresh_id").addClass('hidden');
            $("#occurance_thresh_p").addClass('hidden');
        }  
     }

     $("#landsat8").click(function(){
        satellite = 'landsat8'
        $("#terrain_correction_id").hide();
        $("#speckle_filter_id").hide();
        $("#cloud_mask_id").show();
        $("#terrain_correction_p").hide();
        $("#speckle_filter_p").hide();
        $("#cloud_mask_p").show();
        $('button').removeClass('active');
        $(this).addClass('active');
        check_flood(water_period, flood_val);
    })

     $("#sentinel1").click(function(){
        satellite = 'sentinel1';
        $("#terrain_correction_id").show()
        $("#speckle_filter_id").show();
        $("#cloud_mask_id").hide();
        $("#terrain_correction_p").show();
        $("#speckle_filter_p").show();
        $("#cloud_mask_p").hide();
        $('button').removeClass('active');
        $(this).addClass('active'); 
        check_flood(water_period, flood_val);
     })

     $("#terrain_correction_id").click(function(){
        terr_val = $("#terrain_correction_check").is(':checked') ? 'yes' : 'no'
    })

    $("#speckle_filter_id").click(function(){
        spec_val = $("#speckle_filter_check").is(':checked') ? 'yes' : 'no'
    })

    $("#cloud_mask_id").click(function(){
        cloud_val = $("#cloud_mask_check").is(':checked') ? 'yes' : 'no'
    })

    $("#extract_flood_id").click(function(){
        flood_val = $("#extract_flood_check").is(':checked') ? 'yes' : 'no'
        check_flood(water_period, flood_val);
    })

    $("#water_period_id").change(function(){
        water_period = $("#water_period_id").val();
        if (water_period == '1'){
            $("#occurance_thresh_id").addClass('hidden');
            $("#occurance_thresh_p").addClass('hidden');
        }
        else {
            $("#occurance_thresh_id").removeClass('hidden');
            $("#occurance_thresh_p").removeClass('hidden');
        }
    })

     $("#load_data").click(function(){
         if(input_spatial == ''){
            $.notify("REQUEST FAILED: Please select an area of interest", "warn");
            return
         }

         let dataset = satellite;
         let end_date = $('#end_date').val();
         let start_date = $('#start_date').val();
         let red_method = $('#reducer').val();
         let terrain =  terr_val;
         let speckle =  spec_val;
         let cloud = cloud_val;
         let occurance_thresh = $("#occurance_thresh_id").val();

         var request_obj={
             'input_spatial':input_spatial,
             'dataset' : dataset,
             'start_date': start_date,
             'end_date': end_date,
             'red_method': red_method,
             'terrain': terrain,
             'speckle': speckle,
             'cloud': cloud,
             'flood_val': flood_val,
             'water_period': water_period,
             'occurance_thresh': occurance_thresh

         }

         console.log(request_obj);
         $("#GeneralLoading").removeClass("hidden");
         $.ajax({
             type:"GET",
             url:'get-image-layer/',
             datatype:"JSON",
             data:request_obj,
             success: function(data){
                console.log(data)
                if (data["success"] === true) {
                    $.notify("SUCCESS", "success");
                    $("#GeneralLoading").addClass("hidden");
                    water_layer.setUrl(data.water_url);
                    flood_layer.setUrl(data.flood_url);
                    image_layer.setUrl(data.image_url);
                    map.addLayer(water_layer);
                    map.addLayer(image_layer);
                    $("#export_data").removeClass("hidden");
                }
                else {
                    $.notify("REQUEST FAILED: " + data["error"], "error");
                    $("#GeneralLoading").addClass("hidden");
                    $("#export_data").addClass("hidden");
                }
             },
             error: function(error){
                $.notify("REQUEST FAILED: " + data["error"], "error");
                 console.log(error)
                 $("#GeneralLoading").addClass("hidden");
                 $("#export_data").addClass("hidden");
             }
         })
     })

     $("#clear_data").click(function(){
        water_layer.setUrl('');
        map.removeLayer(water_layer);
        image_layer.setUrl('');
        map.removeLayer(image_layer);
        drawnItems.clearLayers();
        input_spatial ="";
        $("#export_data").addClass("hidden");
     })

     $("#export_data").click(function(){
         let dataset = satellite;
         let end_date = $('#end_date').val();
         let start_date = $('#start_date').val();
         let red_method = $('#reducer').val();
         let terrain =  terr_val;
         let speckle =  spec_val;
         let cloud = cloud_val;
         let occurance_thresh = $("#occurance_thresh_p").val();

         var request_obj={
             'input_spatial':input_spatial,
             'dataset' : dataset,
             'start_date': start_date,
             'end_date': end_date,
             'red_method': red_method,
             'terrain': terrain,
             'speckle': speckle,
             'cloud': cloud,
             'flood_val': flood_val,
             'water_period': water_period,
             'occurance_thresh': occurance_thresh
         }

         console.log(request_obj);
         $("#GeneralLoading").removeClass("hidden");
         $.ajax({
             type:"GET",
             url:'get-export/',
             datatype:"JSON",
             data:request_obj,
             success: function(data){
                console.log(data)
                 if (data["success"] === true) {
                    $.notify("SUCCESS", "success");
                    $("#GeneralLoading").addClass("hidden");
                    window.open(data["export_url"], '_blank');
                 }
                 else {
                    $.notify("REQUEST FAILED: " + data["error"], "error");
                    $("#GeneralLoading").addClass("hidden");
                 }
                
             },
             error: function(error){
                $.notify("REQUEST FAILED: " + data["error"], error);
                 console.log(error)
                 $("#GeneralLoading").addClass("hidden");
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
