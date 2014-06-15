$(function() {
	var map, oldZoom, stats = {};
	
	var parties = ['Green', 'Bloc'];

	$.each(parties, function(i, party) {
		$.ajax('./totals/' + party + '.json', {
			complete : function(xhr, status) {
				stats[party] = xhr.responseJSON;
				if (i == 0) initMap(party);
			}
		});
	});

	function initMap(party) {
		var pstats = stats[party];
		
		// Enabling new cartography and themes
		google.maps.visualRefresh = true;

		// Setting starting option of map to Canada
		var mapOptions = {
			center : new google.maps.LatLng(53, -95),
			zoom : 4,
			mapTypeId : google.maps.MapTypeId.ROADMAP
		};

		// Getting map DOM element
		var mapElement = document.getElementById('mapDiv');

		// Creating a map with DOM element which is just //obtained
		map = new google.maps.Map(mapElement, mapOptions);
		oldZoom = map.getZoom();

		// First, create an object containing LatLng and population for each
		// city.
		var postalCodes = {};
		var circles = [];

		for (var i = 0; i < pstats.length; i++) {
			var circleOptions = {
				strokeColor : 'purple',
				strokeOpacity : 1,
				strokeWeight : 1,
				fillColor : 'yellow',
				//fillOpacity : Number(stats[i]['Amount']) / 5000,
				fillOpacity: .25,
				map : map,
				center : new google.maps.LatLng(
						Number(pstats[i]['Lat']), Number(pstats[i]['Lng'])),
				radius : Number(pstats[i]['Amount']) * 50 / oldZoom
			};
			// Add the circle for this city to the map.
			postalCode = new google.maps.Circle(circleOptions);
			circles.push(postalCode);
		}

		google.maps.event.addListener(map, 'zoom_changed', function(e) {
			var newZoom = map.getZoom();
			for (var i = 0; i < circles.length; i++) {
				console.log(circles[i].getRadius());
				circles[i].setRadius((circles[i].getRadius() * oldZoom)
						/ newZoom);
				console.log(circles[i].getRadius());
			}
			oldZoom = newZoom;
		});
	}
});
