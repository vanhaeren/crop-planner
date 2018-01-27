var map, infoWindow;
var allMeasures = new Array();
// Create a measure object to store our markers, MVCArrays, lines and polygons
var measure = {
    mvcLine: new google.maps.MVCArray(),
    mvcPolygon: new google.maps.MVCArray(),
    mvcMarkers: new google.maps.MVCArray(),
    lengths: [],
    line: null,
    polygon: null,
    color: null
};
allMeasures.push(measure)
var measureIndex  = 0

// When the document is ready, create the map and handle clicks on it
jQuery(document).ready(function() {

    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 15,
        center: new google.maps.LatLng(39.57592, -105.01476),
        mapTypeId: 'hybrid',
        draggableCursor: "crosshair" // Make the map cursor a crosshair so the user thinks they should click something
    });
    infoWindow = new google.maps.InfoWindow;

    if (navigator.geolocation) {
       navigator.geolocation.getCurrentPosition(function(position) {
            var pos = {
              lat: position.coords.latitude,
              lng: position.coords.longitude
            };

            map.setCenter(pos);
          }, function() {
            handleLocationError(true, infoWindow, map.getCenter());
          });
    } else {
       // Browser doesn't support Geolocation
       handleLocationError(false, infoWindow, map.getCenter());
    }

    function handleLocationError(browserHasGeolocation, infoWindow, pos) {
        infoWindow.setPosition(pos);
        infoWindow.setContent(browserHasGeolocation ?
                              'Error: The Geolocation service failed.' :
                              'Error: Your browser doesn\'t support geolocation.');
        infoWindow.open(map);
    }

    google.maps.event.addListener(map, "click", function(evt) {
        // When the map is clicked, pass the LatLng obect to the measureAdd function
        measureAdd(evt.latLng,allMeasures[measureIndex]);
    });
    jQuery.getJSON('http://localhost:5000/planner/user', function(data){
      for (var key in data) {
        for (var i = 0; i < data[key].length; i++) {
           pos =  new google.maps.LatLng(data[key][i].lat,data[key][i].lng)
           measureAdd(pos,allMeasures[measureIndex]);
        }
        measureReset();
    }
    });
});

function measureAdd(latLng,cMeasure) {

    // Add a draggable marker to the map where the user clicked
    var marker = new google.maps.Marker({
        map: map,
        position: latLng,
        draggable: true,
        raiseOnDrag: false,
        title: "Drag me to change shape",
        icon: new google.maps.MarkerImage("/static/img/measure-vertex.png", new google.maps.Size(9, 9), new google.maps.Point(0, 0), new google.maps.Point(5, 5))
    });

    // Add this LatLng to our line and polygon MVCArrays
    // Objects added to these MVCArrays automatically update the line and polygon shapes on the map
    cMeasure.mvcLine.push(latLng);
    cMeasure.mvcPolygon.push(latLng);

    // Push this marker to an MVCArray
    // This way later we can loop through the array and remove them when measuring is done
    cMeasure.mvcMarkers.push(marker);

    // Get the index position of the LatLng we just pushed into the MVCArray
    // We'll need this later to update the MVCArray if the user moves the cMeasure vertexes
    var latLngIndex = cMeasure.mvcLine.getLength() - 1;

    // When the user mouses over the cMeasure vertex markers, change shape and color to make it obvious they can be moved
    google.maps.event.addListener(marker, "mouseover", function() {
        marker.setIcon(new google.maps.MarkerImage("/static/img/measure-vertex-hover.png", new google.maps.Size(15, 15), new google.maps.Point(0, 0), new google.maps.Point(8, 8)));
    });

    // Change back to the default marker when the user mouses out
    google.maps.event.addListener(marker, "mouseout", function() {
        marker.setIcon(new google.maps.MarkerImage("/static/img/measure-vertex.png", new google.maps.Size(9, 9), new google.maps.Point(0, 0), new google.maps.Point(5, 5)));
    });

    // When the cMeasure vertex markers are dragged, update the geometry of the line and polygon by resetting the
    //     LatLng at this position
    google.maps.event.addListener(marker, "drag", function(evt) {
        cMeasure.mvcLine.setAt(latLngIndex, evt.latLng);
        cMeasure.mvcPolygon.setAt(latLngIndex, evt.latLng);
    });

    // When dragging has ended and there is more than one vertex, cMeasure length, area.
    google.maps.event.addListener(marker, "dragend", function() {
        if (cMeasure.mvcLine.getLength() > 1) {
            cMeasureCalc();
        }
    });
    // If there is more than one vertex on the line
    if (cMeasure.mvcLine.getLength() > 1) {

        // If the line hasn't been created yet
        if (!cMeasure.line) {
            if (!cMeasure.color) {
              cMeasure.color = getRandomColor()
            }

            // Create the line (google.maps.Polyline)
            cMeasure.line = new google.maps.Polyline({
                map: map,
                clickable: false,
                strokeColor: cMeasure.color,
                strokeOpacity: 1,
                strokeWeight: 3,
                path:cMeasure.mvcLine
            });

        }

        // If there is more than two vertexes for a polygon
        if (cMeasure.mvcPolygon.getLength() > 2) {

            // If the polygon hasn't been created yet
            if (!cMeasure.polygon) {

                // Create the polygon (google.maps.Polygon)
                cMeasure.polygon = new google.maps.Polygon({
                    clickable: false,
                    map: map,
                    fillOpacity: 0.25,
                    strokeOpacity: 0,
                    paths: cMeasure.mvcPolygon
                });

            }

        }

    }

    // If there's more than one vertex, cMeasure length, area.
    if (cMeasure.mvcLine.getLength() > 1) {
        measureCalc(cMeasure);
    }

}

function measureCalc(cMeasure) {

    // Use the Google Maps geometry library to cMeasure the length of the line
    var length = google.maps.geometry.spherical.computeLength(cMeasure.line.getPath());
    cMeasure.lengths.push(length.toFixed(1));
    //jQuery("#new-lengths").text(length.toFixed(1))
    jQuery("#new-lengths").val(encodeURIComponent(JSON.stringify(cMeasure.lengths)));

    // If we have a polygon (>2 vertexes in the mvcPolygon MVCArray)
    if (cMeasure.mvcPolygon.getLength() > 2) {
        // Use the Google Maps geometry library to cMeasure the area of the polygon
        var area = google.maps.geometry.spherical.computeArea(cMeasure.polygon.getPath());
        jQuery("#span-area").text(area.toFixed(1));
        jQuery("#new-area").val(area.toFixed(1));
        jQuery("#new-coordinates").val(encodeURIComponent(JSON.stringify(cMeasure.mvcPolygon.getArray())));
    }

}

function measureReset() {
    // create new area
    measureIndex += 1;
    var dMeasure = {
        mvcLine: new google.maps.MVCArray(),
        mvcPolygon: new google.maps.MVCArray(),
        mvcMarkers: new google.maps.MVCArray(),
        lengths: [],
        line: null,
        polygon: null,
        color: null
    };
    allMeasures.push(dMeasure)
    //save old measures and draw them
    var clone = jQuery.extend(true, {}, measure);
    clone.mvcLine = jQuery.extend(true, {}, measure.mvcLine);
    clone.mvcPolygon = jQuery.extend(true, {}, measure.mvcPolygon);
    clone.mvcMarkers = jQuery.extend(true, {}, measure.mvcMarkers);

}

function getRandomColor() {
  var letters = '0123456789ABCDEF';
  var color = '#';
  for (var i = 0; i < 6; i++) {
    color += letters[Math.floor(Math.random() * 16)];
  }
  return color;
}