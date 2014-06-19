$(function() {
	// Enable new cartography and themes
	google.maps.visualRefresh = true;

	// Create map centred on Canada
	var mapOptions = {
		center: new google.maps.LatLng(53, -95),
		zoom: 4,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	var map = new google.maps.Map(document.getElementById('mapDiv'), mapOptions);
	var oldZoom = map.getZoom();
	var circles = [];

	// Resize circles when zoom changed
	google.maps.event.addListener(map, 'zoom_changed', function(e) {
		var newZoom = map.getZoom();
		$.each(circles, function(i, circle) {
			circle.setRadius((circle.getRadius() * oldZoom) / newZoom);
		})
		oldZoom = newZoom;
	});

	// Load postal code data for each party and draw the first one
	var parties = [
		['Bloc Que\u0301be\u0301cois', 'blue'],
		['Green Party', 'green']
	];
	var totals = {};
	
	$.get('./totals/totals.json', function(data) {
		totals = data;
		$.each(parties, function(i, party) {
			if (totals.hasOwnProperty(party[0])) {
				$('<a>' + party[0] + '</a>').appendTo('#partyList').click(function(e) {
					e.preventDefault();
					draw_circles(party[0], party[1]);
				});
			}
		});
		
		$('a:first').click();
	});
	
	function draw_circles(party, colour) {
		var ptotals = totals[party];

		// Clear existing circles
		$.each(circles, function(i, circle) {
			circle.setMap(null);
		})

		// Add a circle to the map for each postal code.
		for (var i = 0; i < ptotals.length; i++) {
			var circleOptions = {
				strokeColor: colour,
				strokeOpacity: 1,
				strokeWeight: 1,
				fillColor: colour,
				fillOpacity: .25,
				map: map,
				center: new google.maps.LatLng(Number(ptotals[i]['Lat']),
						Number(ptotals[i]['Lng'])),
				radius: Number(ptotals[i]['Amount']) * 50 / oldZoom
			};
			circles.push(new google.maps.Circle(circleOptions));
		}
	}
});
