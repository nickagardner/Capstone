var map;
var marker; 
var end_marker;

var directionsService = new google.maps.DirectionsService();
var bounds = new google.maps.LatLngBounds();
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

function codeAddress(address) {
  return new Promise((resolve, reject) => {
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == 'OK') {
        const coords = results[0].geometry.location;
        resolve([coords.lat(), coords.lng()]);
      } else {
        resolve(null);
      }
    });
});
};

$("#transcribe").click(function () {
  // recognition.lang = select_dialect.value;
  recognition.start();
});

async function initMap(lat, lon) {
  const { Map } = await google.maps.importLibrary("maps");
  const myLatLng = { lat: lat, lng: lon };
  recognition = new webkitSpeechRecognition();

  recognition.onresult = function(event) {
    var final_transcript = '';
    for (var i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        final_transcript += event.results[i][0].transcript;
      }
    }
    $("#todo").val(final_transcript);
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
    calcRoute();
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
}

function distance(waypoint_coords, end_coords) {
  return ((end_coords[0] - waypoint_coords[0])**2 + (end_coords[1] - waypoint_coords[1])**2)**0.5
}

async function calcRoute() {
  const jsonResponse = await fetch('/static/js/changes.json').then(response => response.json());

  var start = document.getElementById('start').value;
  var start_coords = await codeAddress(start);
  var end = document.getElementById('end').value;
  var end_coords = await codeAddress(end);

  var bad_waypoint_inds = [];
  var bad_avoid_inds = [];

  var waypoints;
  var more_waypoints = "";
  var avoid;
  var avoid_str = "";
  var path_type;
  var api_key;
  var coords;
  var coord_array = [];
  var dist_array = [];
  if (jsonResponse != null) {
    waypoints = jsonResponse.waypoints;

    if (waypoints.length > 0) {
      for (var i=0; i < waypoints.length; i++) {
        coords = await codeAddress(waypoints[i]);
        if (coords != null) {
          coord_array.push(coords);
          dist_array.push(distance(coords, end_coords));
        } else {
          bad_waypoint_inds.push(i);
          console.log("Unable to geocode waypoint: " + waypoints[i])
        }
      };

      coord_array.sort(function(a, b){  
        return dist_array[coord_array.indexOf(b)] - dist_array[coord_array.indexOf(a)];
      });

      for (var i=0; i < coord_array.length; i++) {
        more_waypoints += coord_array[i].join(",");
        more_waypoints += "|";
      };
    };

    avoid = jsonResponse.avoid;
    var avoid_success = 0;
    if (avoid.length > 0) {
      avoid_str = "";
      for (var i=0; i < avoid.length; i++) {
        coords = await codeAddress(avoid[i]);
        if (coords != null) {
          avoid_str = avoid_str + "location:" + coords.join(",");
          if (i < avoid.length - 1) {
            avoid_str += "|";
          };
          avoid_success += 1;
        } else {
          bad_avoid_inds.push(i);
          console.log("Unable to geoscode avoid: " + avoid[i])
        };
      };
      if (avoid_success > 0) {
        avoid_str = "avoid=" + avoid_str + "&";
      }
    }

    path_type = jsonResponse.path_type;
    if (path_type == "") {
      path_type = "bicycle";
    }
    api_key = jsonResponse.api_key;

    console.log(bad_avoid_inds)
    console.log(bad_waypoint_inds)

    $.ajax({
      type:'POST',
      url:'/clean',
      contentType:'application/json',
      dataType : 'json',
      data: JSON.stringify([{bad_waypoint_inds, bad_avoid_inds}]),
    });
  }

  const url = `https://api.geoapify.com/v1/routing?waypoints=${start_coords.join(',')}|${more_waypoints}${end_coords.join(',')}&mode=${path_type}&${avoid_str}details=route_details&apiKey=${api_key}`;
  console.log(url)

  map.data.forEach(function(feature) {
    map.data.remove(feature);
  });

  fetch(url).then(res => res.json()).then(result => {
      map.data.addGeoJson(result);
  }, error => console.log(err));
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