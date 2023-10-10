var map;
var marker; 
var end_marker;
// var mouse_marker;

var directionsService = new google.maps.DirectionsService();
var bounds = new google.maps.LatLngBounds();
var geocoder;
// var renderers = [];

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
        reject(status);
      }
    });
});
}

// async function codeAddress(address, api_key) {
//   let url = `https://api.geoapify.com/v1/geocode/search?text=${address}&apiKey=${api_key}`
//   return await fetch(url).then(res => res.json());
// };

async function initMap(lat, lon) {
  const { Map } = await google.maps.importLibrary("maps");
  const myLatLng = { lat: lat, lng: lon };

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

  // mouse_marker = new google.maps.Marker({
  //   map,
  //   title: "Mouse",
  // });

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

  // google.maps.event.addListener(map, 'mousemove', function (event) {
  //   document.getElementById('lat').innerHTML = event.latLng.lat().toFixed(3) 
  //   document.getElementById('lng').innerHTML = event.latLng.lng().toFixed(3)
  //   // do something with event.latLng
  // });

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

  // google.maps.event.addListener(marker, 'position_changed', function(){
  //     var lat = marker.getPosition().lat();
  //     var lng = marker.getPosition().lng();

  //     $('#lat').val(lat);
  //     $('#lng').val(lng);
  // });

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

  var waypoints;
  var more_waypoints = "";
  var avoid;
  var avoid_str = "";
  var path_types;
  var api_key;
  var coords;
  var coord_array = [];
  var dist_array = [];
  if (jsonResponse != null) {
    waypoints = jsonResponse.waypoints;

    if (waypoints.length > 0) {
      for (var i=0; i < waypoints.length; i++) {
        coords = await codeAddress(waypoints[i])
        coord_array.push(coords);
        dist_array.push(distance(coords, end_coords))
      };

      console.log(coord_array)
      console.log(dist_array)

      coord_array.sort(function(a, b){  
        return dist_array[coord_array.indexOf(b)] - dist_array[coord_array.indexOf(a)];
      });

      console.log(coord_array)

      for (var i=0; i < coord_array.length; i++) {
        more_waypoints += coord_array[i].join(",");
        more_waypoints += "|"
      };
    };

    avoid = jsonResponse.avoid;
    if (avoid.length > 0) {
      avoid_str = "avoid=location:";
      for (var i=0; i < avoid.length; i++) {
        coords = await codeAddress(avoid[i]);
        avoid_str += coords.join(",");
        if (i < avoid.length - 1) {
          avoid_str += "|"
        }
      };
      avoid_str += "&"
    }

    path_types = jsonResponse.path_types;
    api_key = jsonResponse.api_key;
  }
  // for (var j = 0; j < renderers.length; j++) {
  //   renderers[j].set('directions', null);
  // }

  // renderers = [];
  // end_coords = end_coords.features[0].geometry.coordinates.reverse();
  // var request = {
  //   origin: start,
  //   destination: end,
  //   provideRouteAlternatives: true,
  //   travelMode: 'BICYCLING',
  //   waypoints: waypoints,
  //   optimizeWaypoints: true,
  //   // waypoints: [
  //   //   {
  //   //     location: 'Joplin, MO',
  //   //     stopover: false
  //   //   },{
  //   //     location: 'Oklahoma City, OK',
  //   //     stopover: true
  //   //   }],
  // };
  const url = `https://api.geoapify.com/v1/routing?waypoints=${start_coords.join(',')}|${more_waypoints}${end_coords.join(',')}&mode=bicycle&${avoid_str}details=route_details&apiKey=${api_key}`;
  console.log(url)

  map.data.forEach(function(feature) {
    map.data.remove(feature);
  });

  fetch(url).then(res => res.json()).then(result => {
      map.data.addGeoJson(result);
  }, error => console.log(err));

    // directionsService.route(request, function(result, status) {
    //   if (status == 'OK') {
    //     console.log(result)
    //     let routes = result["routes"]
    //     for (var i=0; i < routes.length; i++) {
    //       if (i == 0) {
    //         var directionsRenderer = new google.maps.DirectionsRenderer({suppressMarkers: true});
    //       } else{
    //         var directionsRenderer = new google.maps.DirectionsRenderer({suppressMarkers: true,});
    //         directionsRenderer.setOptions({polylineOptions: {strokeColor: '#808080', strokeOpacity: 1}}); 
    //       }
    //       directionsRenderer.setMap(map);
    //       directionsRenderer.setRouteIndex(i);
    //       directionsRenderer.setDirections(result);
    //       renderers.push(directionsRenderer)
    //     }
    //   }});;
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