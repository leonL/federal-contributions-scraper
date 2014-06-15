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
	var parties = {
		'Green': ['Green Party', 'green'],
		'Bloc': ['Bloc Quebecois', 'blue']
	};
	var stats = {};
	
	$.each(Object.keys(parties).sort(), function(i, party) {
		$.ajax('./totals/' + party + '.json', {
			complete: function(xhr, status) {
				stats[party] = xhr.responseJSON;
				if (i == 0)
					draw_circles(party);

				// Create a link for each party
				$('<a data-party="' + party + '">' + parties[party][0] + '</a>')
						.appendTo('#partyList').click(function(e) {
					e.preventDefault();
					draw_circles($(this).attr('data-party'));
				});
			}
		});
	});

	function draw_circles(party) {
		var pstats = stats[party];
		var colour = parties[party][1];

		// Clear existing circles
		$.each(circles, function(i, circle) {
			circle.setMap(null);
		})

		// Add a circle to the map for each postal code.
		for (var i = 0; i < pstats.length; i++) {
			var circleOptions = {
				strokeColor: colour,
				strokeOpacity: 1,
				strokeWeight: 1,
				fillColor: colour,
				fillOpacity: .25,
				map: map,
				center: new google.maps.LatLng(Number(pstats[i]['Lat']),
						Number(pstats[i]['Lng'])),
				radius: Number(pstats[i]['Amount']) * 50 / oldZoom
			};
			circles.push(new google.maps.Circle(circleOptions));
		}
	}
});
