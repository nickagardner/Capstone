var map;
var marker; 
var end_marker;
var myLatLng;

var bounds;
var defaultBounds;
var geocoder;
var recognition;

var start_box;
var end_box;

var svgMarker;
var markers = [];

function coordToAddress(latlng) {
  geocoder
    .geocode({ location: latlng })
    .then((response) => {
      if (response.results[0]) {
        document.getElementsByName('start')[0].value = response.results[0].formatted_address
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
    statusCode: {
      200: function (data) {
        renderRoute(data)
      },
      201: function (data) {
        renderWindows(data)
      },
    },
  });
}

async function initMap(lat, lon) {
  const { Map } = await google.maps.importLibrary("maps");
  myLatLng = { lat: lat, lng: lon };
  bounds = new google.maps.LatLngBounds();

  svgMarker = {
    path: "M224 32H64C46.3 32 32 46.3 32 64v64c0 17.7 14.3 32 32 32H441.4c4.2 0 8.3-1.7 11.3-4.7l48-48c6.2-6.2 6.2-16.4 0-22.6l-48-48c-3-3-7.1-4.7-11.3-4.7H288c0-17.7-14.3-32-32-32s-32 14.3-32 32zM480 256c0-17.7-14.3-32-32-32H288V192H224v32H70.6c-4.2 0-8.3 1.7-11.3 4.7l-48 48c-6.2 6.2-6.2 16.4 0 22.6l48 48c3 3 7.1 4.7 11.3 4.7H448c17.7 0 32-14.3 32-32V256zM288 480V384H224v96c0 17.7 14.3 32 32 32s32-14.3 32-32z",
    fillColor: "red",
    fillOpacity: 0.7,
    strokeWeight: 1,
    rotation: 0,
    scale: 0.075,
    anchor: new google.maps.Point(0, 10),
  };

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

  defaultBounds = new google.maps.LatLngBounds(
    new google.maps.LatLng(lat-0.2, lon+0.2),
    new google.maps.LatLng(lat+0.2, lon+0.2));
  
  var start = document.getElementById('start');
  
  start_box = new google.maps.places.SearchBox(start, {
    bounds: defaultBounds
  });

  var end = document.getElementById('end');
  
  end_box = new google.maps.places.SearchBox(end, {
    bounds: defaultBounds
  });

  google.maps.event.addListener(start_box, 'places_changed', function(){
    refitBounds();
    if (end_box.getPlaces().length > 0) {
      requestRoute();
    };
    myLatLng = start_box.getPlaces()[0].geometry.location;
  });

  google.maps.event.addListener(end_box, 'places_changed', function(){
    refitBounds();
    requestRoute();
  });

  geocoder = new google.maps.Geocoder();
  coordToAddress(myLatLng)
  
  $(document).on('submit','#todo-form',function(e) {
    e.preventDefault();
    if (markers.length > 0) {
      clear();
    };
    requestRoute();
  });

  $(document).on('submit','#clear-button',function(e) {
    e.preventDefault();
    if (markers.length > 0) {
      clear();
    };
    if ($("#end").val() != "") {
      requestRoute(true);
    };
    $("#todo").val("");
  });
}

async function refitBounds() {
  bounds = new google.maps.LatLngBounds();

  try{
    var places = start_box.getPlaces();
    var i, place;
    for(var i=0; place=places[i];i++){
      bounds.extend(place.geometry.location);
      marker.setPosition(place.geometry.location);
    };
  } catch(err) {
    bounds = new google.maps.LatLngBounds(
      new google.maps.LatLng(myLatLng.lat-0.01, myLatLng.lng-0.01),
      new google.maps.LatLng(myLatLng.lat+0.01, myLatLng.lng+0.01));
  }

  try {
    var places = end_box.getPlaces();
    var i, place;

    for(i=0; place=places[i];i++){
      bounds.extend(place.geometry.location);
      end_marker.setPosition(place.geometry.location);
    };
  } catch(err) {
    console.log(err)
  }
  map.fitBounds(bounds);
  map.panToBounds(bounds);
}

async function clear () {
  for (var i=0;i<markers.length;i++) {
    markers[i].setMap(null);
  }
  markers = [];
  refitBounds();
}

async function renderRoute(route_features) {
  console.log(route_features)
  map.data.forEach(function(feature) {
    map.data.remove(feature);
  });

  map.data.addGeoJson(route_features);
};

function setEndAndRequest(end) {
  $("#end").val(end);
  requestRoute();
};

async function renderWindows(route_features) {
  map.data.forEach(function(feature) {
    map.data.remove(feature);
  });

  let trails = route_features.data

  for (var i = 0; i < trails.length; i++) {
    const contentString =
    '<div id="content">' +
    '<div id="siteNotice">' +
    "</div>" +
    '<h1 id="firstHeading" class="firstHeading">' + trails[i].name + '</h1>' +
    '<div style="text-align: center" id="imageContent">' +

    '<img width="300" height="300" src="' + trails[i].thumbnail + '"></img>' + 
    "</div>" +
    '<div id="bodyContent">' +
    "<p>" + trails[i].description + "</p>" +
    '<p><b>Length:</b> ' + trails[i].length + '</p>' +
    '<p><b>Difficulty:</b> ' + trails[i].difficulty + '</p>' +
    '<p><b>Rating:</b> ' + trails[i].rating + '</p>' +
    "</div>" +
    "</div>";

    bounds.extend({ lat: Number(trails[i].lat), lng: Number(trails[i].lon)});

    const infowindow = new google.maps.InfoWindow({
      content: contentString,
      ariaLabel: trails[i].name,
      maxWidth: 400,
    });
    const marker = new google.maps.Marker({
      position: { lat: Number(trails[i].lat), lng: Number(trails[i].lon)},
      map,
      title: trails[i].name,
      icon: svgMarker
    });

    markers.push(marker)
  
    marker.addListener("click", () => {
      infowindow.open({
        anchor: marker,
        map,
      });
    });
  };
  map.fitBounds(bounds);
  map.panToBounds(bounds);
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