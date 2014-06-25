$(function() {
	var parties = [
		['Bloc Que\u0301be\u0301cois', 'deepskyblue'],
		['Conservative Party', 'blue'],
		['Green Party', 'green'],
		['Liberal Party', 'red'],
		['New Democratic Party', 'orange'],
	];

	
	// enable new cartography and themes
	google.maps.visualRefresh = true;

	// create map centred on Canada
	var mapOptions = {
		center: new google.maps.LatLng(53, -95),
		zoom: 4,
		mapTypeId: google.maps.MapTypeId.ROADMAP
	};
	var map = new google.maps.Map(document.getElementById('mapDiv'), mapOptions);
	var oldZoom = map.getZoom();
	var circles = [];

	// resize circles when zoom changed
	google.maps.event.addListener(map, 'zoom_changed', function(e) {
		var newZoom = map.getZoom();
		$.each(circles, function(i, circle) {
			circle.setRadius((circle.getRadius() * oldZoom) / newZoom);
		})
		oldZoom = newZoom;
	});


	// load amounts for each party and draw links for each of them
	$.get('./results/postal_groups.json', function(json) {
		$.each(parties, function(i, pdata) {
			party = pdata[0];
			colour = pdata[1];
			
			if (json.hasOwnProperty(party)) {
				var data = {party: party, colour: colour, amounts: json[party]}
				$('<a>' + party + '</a>').appendTo('#partyList').click(data, function(e) {
					e.preventDefault();
					draw_circles(e.data.party, e.data.colour, e.data.amounts);
				});
			}
		});
		
		$('a:first').click();
	});
	
	
	// draw circles on the map for one party
	function draw_circles(party, colour, amounts) {
		var minSize = 20;
		var scale = 10;

		// Clear existing circles
		$.each(circles, function(i, circle) {
			circle.setMap(null);
		})

		// Add a circle to the map for each postal code.
		for (var i = 0; i < amounts.length; i++) {
			var radius = (minSize + Number(amounts[i]['Amount'])) * scale / oldZoom;
			
			var circleOptions = {
				strokeColor: colour,
				strokeOpacity: 1,
				strokeWeight: 1,
				fillColor: colour,
				fillOpacity: .25,
				map: map,
				center: new google.maps.LatLng(
						Number(amounts[i]['Lat']),
						Number(amounts[i]['Lng'])),
				radius: radius
			};
			circles.push(new google.maps.Circle(circleOptions));
		}
	}
});
