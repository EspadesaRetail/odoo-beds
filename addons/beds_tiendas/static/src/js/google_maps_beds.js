var infowindow;
var markers = [];
var zoom;
var ZOOM_MIN = 6;
var ZOOM_MAX = 15;
var input;
var searchBox;
var autocomplete;

function initTiendasBeds() {
    var myLatLng = {lat: 40.4380637, lng: -3.7497478};

    var mymap = document.getElementById('map');
    console.log("Init Map Tiendas bed's");
    var map = new google.maps.Map(document.getElementById('map'), {
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        center: myLatLng,
    });

    // Create the search box and link it to the UI element.
    input = document.getElementById('pac-input');
    searchBox = new google.maps.places.SearchBox(input);

    // Bias the SearchBox results towards current map's viewport.
    map.addListener('bounds_changed', function () {
        searchBox.setBounds(map.getBounds());
    });

    // SearchBox
    searchMarkers = [];
    searchBox.addListener('places_changed', function () {
        var searchPlace = null;

        var places = searchBox.getPlaces();
        console.log("Places: " + places);
        if (places.length == 0) {
            return;
        }

        searchMarkers.forEach(function (marker) {
            marker.setMap(null);
        });
        searchMarkers = [];

        // For each place, get the icon, name and location.
        var bounds = new google.maps.LatLngBounds();
        places.forEach(function (place) {

            if (place.geometry.viewport) {
                // Only geocodes have viewport.
                bounds.union(place.geometry.viewport);
            } else {
                bounds.extend(place.geometry.location);
            }

            searchPlace = place;

        });
        map.fitBounds(bounds);

        calculateNearestShop(map, searchPlace.geometry.location)
        showShops(map);
    });


    // Búsqueda.
    $("#map_search" ).on( "click", function() {
        console.log("Button search: " + input);
        google.maps.event.trigger(input, 'focus')
        google.maps.event.trigger(input, 'keydown', {keyCode: 13});
    });

    // Localización via geo ip.
    $("#map_locate" ).on( "click", function() {
        console.log("Geo location search");
        $('#pac-input').val('');
        getGeoLocation(map);
    });

    // Ocultar la localización de la web.
    var $location;
    $location = $('#location').each(function( index ) {
        $(this).addClass("hide");
    });

    // [END search]
    zoom = ZOOM_MIN;
    showShops(map);

}

function bindEventClick(gm, marker) {
    google.maps.event.addListener(marker, 'click', function () {
        gm.setCenter(marker.getPosition());
        if (infowindow != null)
            infowindow.close();

        iw = "<div class='infowindow-ovalo'>" +
                "<div class='infowindow-info'>" +
                "<p><img class='infowindow-foto' width='100px' " +
                "src='" + marker.img + "'>" +
                "</p>" +
                "<h3>" + marker.title + "</h3>" +
                "<p><span>" + marker.street +
                "<br>" + marker.phone +
                "<br>CP:" + marker.zip + " - " + marker.city +
                "<br>Email:" + marker.email +
                "<br><br>" + marker.schedule1 +
                "<br>" + marker.schedule2 +
                "<br>" + marker.schedule3 +
                "<br>" + marker.schedule4 +
                "</span></p></div></div>"


        infowindow = new google.maps.InfoWindow({
            content: iw,
            maxWidth: 350
        });
        infowindow.open(gm, marker);
        /*        setTimeout(function () {
         infowindow.close();
         infowindow = null;
         }, 15000);
         */

    });
}


function showShops(map) {

    // Clear markers.
    markers.forEach(function (marker) {
        marker.setMap(null);
    });
    markers = [];

    for (var i = 0; i < partner_data.counter; i++) {
        m = partner_data.partners[i];
        var marker;
        var latlng = new google.maps.LatLng(m.latitude, m.longitude);

        var point = "shop_point.png"
        if (m.nearest.valueOf() == 1)
            point = "nearest_point.png"


        marker = new google.maps.Marker({
            id: m.id,
            map: map,
            position: latlng,
            title: m.name,
            zip: m.zip,
            street: m.street,
            city: m.city,
            state: m.state,
            phone: m.phone,
            email: m.email,
            icon: {
                url: "/beds_theme/static/src/img/icon/" + point,
            },
            img: m.img,
            schedule1: m.schedule1,
            schedule2: m.schedule2,
            schedule3: m.schedule3,
            schedule4: m.schedule4

        });

        markers.push(marker);
        bindEventClick(map, marker);


        // Mostar el infowindow si es la más cercana.
        if (m.nearest.valueOf() == 1)
            new google.maps.event.trigger(marker, 'click');

    }


    map.setZoom(zoom);

}

function calculateNearestShop(map, origin) {
    var R = 6378.137; //Radio de la tierra en km
    rad = function (x) {
        return x * Math.PI / 180;
    };

    if (origin === null)
        return;

    var dest = [];

    for (var i = 0; i < partner_data.counter; i++) {
        m = partner_data.partners[i];
        partner_data.partners[i].nearest = 0;

        if (m.latitude !== 0 && m.longitude !== 0) {

            var loc = {
                index: i,
                name: m.name,
                latitude: m.latitude,
                longitude: m.longitude,
                distance: 0
            }
            dest.push(loc);
        }
    }

    for (var i = 0; i < dest.length; i++) {

        var dLat = rad(dest[i]['latitude'] - origin.lat());
        var dLong = rad(dest[i]['longitude'] - origin.lng());

        var a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(rad(origin.lat())) * Math.cos(rad(dest[i]['latitude'])) * Math.sin(dLong / 2) * Math.sin(dLong / 2);
        var c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        var d = R * c;

        dest[i]['distance'] = d.toFixed(0).valueOf();
    }

    var distance = 9999;
    var dd = 0;
    var index;
    for (var i = 0; i < dest.length; i++) {

        dd = dest[i]['distance'].valueOf();


        if (parseInt(dd) < parseInt(distance)) {
            distance = dd;
            index = dest[i]['index'];
        }
    }

    zoom = ZOOM_MIN;
    if (index >= 0) {
        // Ajustar el zoom en función de la distancia.

        var pow = 1 + Math.pow(Number(distance), 1.5);
        var inc = 1 + Math.floor((ZOOM_MAX - ZOOM_MIN) * (1 / pow));

        zoom = ZOOM_MIN + inc;
        partner_data.partners[index]['nearest'] = 1;
    }

    //console.log("DISTANCIA:" + distance + "\nPOW" + pow + "\nINC" + inc + "\nZOOM:" + zoom);

}



function getGeoLocation(map) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var pos = {
                lat: function () {
                    return position.coords.latitude;
                },
                lng: function () {
                    return position.coords.longitude;
                }
            };

            calculateNearestShop(map, pos)
            showShops(map);


        }, function () {
            //handleLocationError(true, infoWindow, map.getCenter());
        });
    } else {
        // Browser doesn't support Geolocation
        //handleLocationError(false, infoWindow, map.getCenter());
    }
}

function handleLocationError(browserHasGeolocation, infoWindow, pos) {
    infoWindow.setPosition(pos);
    infoWindow.setContent(browserHasGeolocation ?
            'Error: The Geolocation service failed.' :
            'Error: Your browser doesn\'t support geolocation.');
}
