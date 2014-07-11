$(function() {
	var colours = {
		'Bloc Qu\u00e9b\u00e9cois': 'deepskyblue',
		'Conservative Party': 'blue',
		'Green Party': 'green',
		'Liberal Party': 'red',
		'New Democratic Party': 'orange'
	};
	
	
	// enable new cartography and themes
	google.maps.visualRefresh = true;
	
	// create map centred on Canada
	var mapOptions = {
		center: new google.maps.LatLng(60, -98),
		zoom: $('#mapDiv').height() > 400 ? 4 : 3,
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
	
	
	// return a sorted list of an object's keys
	function sorted_index(obj) {
		var index = [];
		for (key in obj) index.push(key);
		index.sort(function(a, b) {
			return a < b ? -1 : (a > b ? 1 : 0);
		});
		return index;
	}
	
	
	// load totals for each party and draw bars for each
	var party_totals = {};
	$.get('./results/totals.json', function(results) {
		$.each(sorted_index(results), function(i, year) {
			$('#years').append('<option>' + year + '</option>');
			$('#partyList').append('<div id="list-' + year + '">');
			
			party_totals[year] = {};
			$.each(sorted_index(results[year]), function(i, party) {
				// skip parties that aren't in this year's results
				if (!results[year].hasOwnProperty(party)) return true;
				party_totals[year][party] = Number(results[year][party]);
			});
		});
		
		$('#years').trigger('change');
	});
	
	
	// load geographical results for each party and generate circles for each
	var party_circles = {};
	$.get('./results/postal_groups.json', function(results) {
		var years = sorted_index(results);
		
		// find largest single result and set scale accordingly
		var max = 1;
		$.each(years, function(i, year) {
			$.each(sorted_index(results[year]), function(i, party) {
				$.each(results[year][party], function(i, pgroup) {
					max = Math.max(max, Number(pgroup['Amount']));
				});
			});
		});
		
		var minSize = 20;
		var scale = 200000000 / max;
		
		// generate circles for each party in each year
		$.each(years, function(i, year) {
			party_circles[year] = {};
			
			$.each(sorted_index(results[year]), function(i, party) {
				party_circles[year][party] = [];
				var colour = colours[party];
				
				$.each(results[year][party], function(i, pgroup) {
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
					party_circles[year][party].push(new google.maps.Circle(circleOptions));
				});
			});
		});
	});
	
	
	$('#years').change(function() {
		var year = $(this).val();
		var parties = sorted_index(party_totals[year]);
		
		// get total for each party and find the maximum
		var max = 1;
		$.each(parties, function(i, party) {
			if (!party_totals[year].hasOwnProperty(party)) return true;
			max = Math.max(max, Number(party_totals[year][party]));
		});
		console.log(party_totals[year]);
		
		// create colour bars for each party
		$.each(parties, function(i, party) {
			if (!party_totals[year].hasOwnProperty(party)) return true;
			$('#partyList #list-' + year).append(
				$('<a>' + party + '</a>').append($('<div>').css({
					width: '' + (party_totals[year][party] / max * 100) + '%',
					backgroundColor: colours[party]
				}))
			);
		});
	});
	
	
	// when party is clicked, show party info and circles
	$('#partyList').on('click', 'a', function(e) {
		e.preventDefault();
		
		if ($(this).hasClass('selected')) return;
		$('a').removeClass('selected');
		$(this).addClass('selected');
		
		var year = $('#years').val();
		var party = $(this).text();
		var colour = colours[party];
		
		// format total amount as a currency string with commas
		var total = (party_totals[year][party] / 100).toFixed(2);
		var offset = total.length % 3;
		var total_text = '$' + total.slice(0, offset);
		for (i = offset; i < total.length - 3; i += 3) {
			total_text += (i > 0 ? ',' : '') + total.slice(i, i + 3);
		}
		total_text += total.slice(-3);
		
		// show info dialog for this party
		$('#info').show();
		$('#info h2').text($(this).text()).css('border-color', colour);
		$('#info #year').text(year);
		$('#info #total').text(total_text).css('color', colour);
		
		// clear existing circles and enable this party's circles
		$.each(circles, function(i, circle) {
			circle.setMap(null);
		});
		circles = party_circles[year][party];
		$.each(circles, function(i, circle) {
			circle.setMap(map);
		});
	});
});
