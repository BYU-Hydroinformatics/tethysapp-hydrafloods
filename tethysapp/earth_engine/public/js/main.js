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

function creationMaps(){
    var vector_obj = {};
    var baseMapsNames = [
        'ArcGIS:DarkGray', 
        'ArcGIS:Navigation',
        'ArcGIS:DarkGray:Base',
        'ArcGIS:NavigationNight',
        'ArcGIS:DarkGray:Labels',
        'ArcGIS:Streets',
        'ArcGIS:LightGray',
        'ArcGIS:StreetsNight',
        'ArcGIS:LightGray:Base',
        'ArcGIS:StreetsRelief',
        'ArcGIS:LightGray:Labels',
        'ArcGIS:StreetsRelief:Base'
    ];
    baseMapsNames.forEach(mp=>{
        var navigationMap = L.esri.Vector.vectorBasemapLayer(mp, {
            apikey: "AAPK052bec1846714415aed2c85ddfa15f73KYexWiKoe0Au2nFQprFm_CWnafrYs4Y3MwTI3iqb-QBEwR808TRyXrudF4Za40V-" // Replace with your API key - https://developers.arcgis.com
        });
        var nameBase = mp.split(':')[1];
        vector_obj[nameBase] = navigationMap;
    })
    return vector_obj

}

// add csrf token to appropriate ajax requests
$(function() {
    //Start Map //
    var map = L.map('map').setView([8.913648, -79.544706], 10);

    var baseMaps = creationMaps();
    console.log(baseMaps)
    L.esri.Vector.vectorBasemapLayer('ArcGIS:Navigation', {
        apikey: "AAPK052bec1846714415aed2c85ddfa15f73KYexWiKoe0Au2nFQprFm_CWnafrYs4Y3MwTI3iqb-QBEwR808TRyXrudF4Za40V-" // Replace with your API key - https://developers.arcgis.com
    }).addTo(map);
    L.control.layers(baseMaps,{},{position: 'bottomleft'}).addTo(map);


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
     map.on(L.Draw.Event.CREATED, function (e) {
        console.log('Draw Event Created');
        drawnItems.addLayer(e.layer);
        input_spatial = JSON.stringify(e.layer.toGeoJSON());
        type_of_series = e.layerType;
      });
 
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", getCookie("csrftoken"));
            }
        }
    });
}); //document ready;
