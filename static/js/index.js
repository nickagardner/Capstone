var map;
var marker; 
var end_marker;

var directionsService = new google.maps.DirectionsService();
var renderers = [];

function geocodeLatLng(geocoder, latlng) {
  geocoder
    .geocode({ location: latlng })
    .then((response) => {
      if (response.results[0]) {
        document.getElementsByName('start')[0].value = response.results[0].formatted_address;
      } else {
        window.alert("No results found");
      }
    })
    .catch((e) => window.alert("Geocoder failed due to: " + e));
}

async function initMap(lat, lon) {
  const { Map } = await google.maps.importLibrary("maps");
  const myLatLng = { lat: lat, lng: lon };

  const geocoder = new google.maps.Geocoder();
  geocodeLatLng(geocoder, myLatLng)

  map = new Map(document.getElementById("map"), {
    center: myLatLng,
    zoom: 15,
  });

  marker = new google.maps.Marker({
    position: myLatLng,
    map,
    title: "Start",
  });

  var defaultBounds = new google.maps.LatLngBounds(
    new google.maps.LatLng(lat-0.2, lon+0.2),
    new google.maps.LatLng(lat+0.2, lon+0.2));
  
  var start = document.getElementById('start');
  
  var start_box = new google.maps.places.SearchBox(start, {
    bounds: defaultBounds
  });

  google.maps.event.addListener(start_box, 'places_changed', function(){

    var places = start_box.getPlaces();
    var bounds = new google.maps.LatLngBounds();
    var i, place;

    for(var i=0; place=places[i];i++){
        bounds.extend(place.geometry.location);
        marker.setPosition(place.geometry.location);
    }

    map.fitBounds(bounds);
    map.setZoom(15);
  });

  var end = document.getElementById('end');
  
  var end_box = new google.maps.places.SearchBox(end, {
    bounds: defaultBounds
  });

  $(document).on('submit','#todo-form',function(e) {
    e.preventDefault();
    $.ajax({
      type:'POST',
      url:'/',
      data:{
        todo:$("#todo").val()
      },
      success: function(data) {
        calcRoute()
      }
    });
  });

  $(document).on('submit','#clear-button',function(e) {
    e.preventDefault();
    $.ajax({
      type:'POST',
      url:'/',
      data:{
        clear: 1
      },
      success: function(data) {
        calcRoute()
      }
    });
    $("#todo").val("");
  });

  google.maps.event.addListener(end_box, 'places_changed', function(){
    var places = end_box.getPlaces();
    var bounds = new google.maps.LatLngBounds();
    var i, place;

    end_marker = new google.maps.Marker({
      map,
      title: "Destination",
    });

    for(i=0; place=places[i];i++){
        bounds.extend(place.geometry.location);
        end_marker.setPosition(place.geometry.location);
    }

    map.fitBounds(bounds);
    map.setZoom(15);
    calcRoute();
  });

  // google.maps.event.addListener(marker, 'position_changed', function(){
  //     var lat = marker.getPosition().lat();
  //     var lng = marker.getPosition().lng();

  //     $('#lat').val(lat);
  //     $('#lng').val(lng);
  // });

}

function calcRoute() {
  fetch('/static/js/changes.json')
  .then(response => response.json())
  .then(jsonResponse => {
    var waypoints;
    if (jsonResponse != null) {
      waypoints = jsonResponse.waypoints
    }
    for (var j = 0; j < renderers.length; j++) {
      renderers[j].set('directions', null);
    }
    renderers = [];
    var start = document.getElementById('start').value;
    var end = document.getElementById('end').value;
    var request = {
      origin: start,
      destination: end,
      provideRouteAlternatives: true,
      travelMode: 'BICYCLING',
      waypoints: waypoints,
      optimizeWaypoints: true,
      // waypoints: [
      //   {
      //     location: 'Joplin, MO',
      //     stopover: false
      //   },{
      //     location: 'Oklahoma City, OK',
      //     stopover: true
      //   }],
    };
    directionsService.route(request, function(result, status) {
      if (status == 'OK') {
        let routes = result["routes"]
        for (var i=0; i < routes.length; i++) {
          if (i == 0) {
            var directionsRenderer = new google.maps.DirectionsRenderer({suppressMarkers: true});
          } else{
            var directionsRenderer = new google.maps.DirectionsRenderer({suppressMarkers: true,});
            directionsRenderer.setOptions({polylineOptions: {strokeColor: '#808080', strokeOpacity: 1}}); 
          }
          directionsRenderer.setMap(map);
          directionsRenderer.setRouteIndex(i);
          directionsRenderer.setDirections(result);
          renderers.push(directionsRenderer)
        }
      }});
  });
}

if ("geolocation" in navigator) {
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lng = position.coords.longitude;

      initMap(lat, lng);
    },
    (error) => {
      console.error("Error getting user location:", error);
    }
  );
} else {
  console.error("Geolocation is not supported by this browser.");
}