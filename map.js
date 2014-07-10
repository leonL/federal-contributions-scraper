$(function() {
	var parties = [
		['Bloc Qu\u00e9b\u00e9cois', 'deepskyblue'],
		['Conservative Party', 'blue'],
		['Green Party', 'green'],
		['Liberal Party', 'red'],
		['New Democratic Party', 'orange']
	];
	var year = '2012';
	
	
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
	
	
	// load totals for each party and draw bars for each
	var party_totals = {};
	$.get('./results/totals.json', function(results) {
		// get total for each party and find the maximum
		var max = 1;
		$.each(parties, function(i, pdata) {
			var party = pdata[0];
			max = Math.max(max, results[party][year]);
		});
		
		// create
		$.each(parties, function(i, pdata) {
			var party = pdata[0];
			var colour = pdata[1];
			var total = Number(results[party][year]);
			var width = total / max * 100;
			
			// format total amount as a currency string
			total = (total / 100).toFixed(2);
			
			var offset = total.length % 3;
			party_totals[party] = '$' + total.slice(0, offset);
			for (i = offset; i < total.length - 3; i += 3) {
				party_totals[party] += (i > 0 ? ',' : '') + total.slice(i, i + 3);
			}
			party_totals[party] += total.slice(-3);
			
			// create colour bar
			$('#partyList').append($('<a>' + party + '</a>').append($('<div>').css({
				width: '' + width + '%',
				backgroundColor: colour
			})));
		});
	});
	
	
	// load geographical results for each party and generate circles for each
	var party_circles = {};
	$.get('./results/postal_groups.json', function(results) {
		// find largest single result and set scale accordingly
		var max = 1;
		$.each(results, function(party, years) {
			$.each(years[year], function(i, result) {
				max = Math.max(max, Number(result['Amount']));
			});
		});
		var minSize = 20;
		var scale = 200000000 / max;
		
		$.each(parties, function(i, pdata) {
			var party = pdata[0];
			var colour = pdata[1];
			
			// generate circles for this party
			party_circles[party] = [];
			$.each(results[party][year], function(i, pgroup) {
				var amount = Number(pgroup['Amount']) / 100;
				var radius = (minSize + amount) * scale / oldZoom;
				var circleOptions = {
					strokeColor: colour,
					strokeOpacity: 1,
					strokeWeight: 1,
					fillColor: colour,
					fillOpacity: .25,
					map: null,
					center: new google.maps.LatLng(
						Number(pgroup['Lat']),
						Number(pgroup['Lng'])
					),
					radius: radius
				};
				party_circles[party].push(new google.maps.Circle(circleOptions));
			});
		});
	});
	
	
	// when party is clicked, show party info and circles
	$('#partyList').on('click', 'a', function(e) {
		e.preventDefault();
		
		if ($(this).hasClass('selected')) return;
		$('a').removeClass('selected');
		$(this).addClass('selected');
		
		var party = $(this).text();
		var colour = $('div', this).css('background-color');
		
		// show info dialog for this party
		$('#info').show();
		$('#info h2').text($(this).text()).css('border-color', colour);
		$('#info #year').text(year);
		$('#info #total').text(party_totals[party]).css('color', colour);
		
		// clear existing circles and enable this party's circles
		$.each(circles, function(i, circle) {
			circle.setMap(null);
		});
		circles = party_circles[party];
		$.each(circles, function(i, circle) {
			circle.setMap(map);
		});
	});

});
