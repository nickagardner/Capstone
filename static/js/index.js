var map;
var marker; 
var end_marker;

var directionsService;
var bounds;
var geocoder;
var recognition;

function geocodeLatLng(latlng) {
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
};

$("#transcribe").click(function () {
  // recognition.lang = select_dialect.value;
  recognition.start();
});

async function requestRoute(clear=false){
  let data_dict = {"start": document.getElementsByName('start')[0].value, 
               "end": document.getElementsByName('end')[0].value,
               "todo": $("#todo").val(),
               "clear": clear,
               "bounds": bounds};
  $.ajax({
    type:'POST',
    url:'/',
    contentType:'application/json',
    dataType : 'json',
    data: JSON.stringify({data_dict}),
    success: function(data) {
      renderRoute(data)
    }
  });
}

async function initMap(lat, lon) {
  const { Map } = await google.maps.importLibrary("maps");
  const myLatLng = { lat: lat, lng: lon };
  bounds = new google.maps.LatLngBounds();
  directionsService = new google.maps.DirectionsService();

  recognition = new webkitSpeechRecognition();

  recognition.onresult = function(event) {
    var final_transcript = '';
    for (var i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        final_transcript += event.results[i][0].transcript;
      }
    }
    $("#todo").val(final_transcript);
    requestRoute();
  };

  geocoder = new google.maps.Geocoder();
  geocodeLatLng(myLatLng)

  map = new Map(document.getElementById("map"), {
    center: myLatLng,
    zoom: 15,
  });

  const bikeLayer = new google.maps.BicyclingLayer()
  bikeLayer.setMap(map);

  marker = new google.maps.Marker({
    position: myLatLng,
    map,
    title: "Start",
  });

  end_marker = new google.maps.Marker({
    map,
    title: "Destination",
  });

  bounds.extend(myLatLng);

  var defaultBounds = new google.maps.LatLngBounds(
    new google.maps.LatLng(lat-0.2, lon+0.2),
    new google.maps.LatLng(lat+0.2, lon+0.2));
  
  var start = document.getElementById('start');
  
  var start_box = new google.maps.places.SearchBox(start, {
    bounds: defaultBounds
  });

  google.maps.event.addListener(start_box, 'places_changed', function(){
    var places = start_box.getPlaces();
    var i, place;

    for(var i=0; place=places[i];i++){
        bounds.extend(place.geometry.location);
        marker.setPosition(place.geometry.location);
    }

    map.fitBounds(bounds);
    map.panToBounds(bounds);
  });

  var end = document.getElementById('end');
  
  var end_box = new google.maps.places.SearchBox(end, {
    bounds: defaultBounds
  });

  google.maps.event.addListener(end_box, 'places_changed', function(){
    var places = end_box.getPlaces();
    var i, place;

    for(i=0; place=places[i];i++){
        bounds.extend(place.geometry.location);
        end_marker.setPosition(place.geometry.location);
    }

    map.fitBounds(bounds);
    map.panToBounds(bounds);
    requestRoute();
  });
  
  $(document).on('submit','#todo-form',function(e) {
    e.preventDefault();
    requestRoute();
  });

  $(document).on('submit','#clear-button',function(e) {
    e.preventDefault();
    requestRoute(clear=True);
    $("#todo").val("");
  });
}

async function renderRoute(route_features) {
  map.data.forEach(function(feature) {
    map.data.remove(feature);
  });

  map.data.addGeoJson(route_features);
};

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