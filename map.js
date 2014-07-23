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
		zoom: $('#mapDiv').height() > 600 ? 4 : 3,
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
		});
		oldZoom = newZoom;
	});
	
	// remove all circles from the map
	function clear_circles() {
		$.each(circles, function(i, circle) {
			circle.setMap(null);
		});
		circles = [];
	}
	
	// return a sorted list of an object's keys
	function sorted_index(obj) {
		var index = [];
		for (key in obj) index.push(key);
		index.sort(function(a, b) {
			return a < b ? -1 : (a > b ? 1 : 0);
		});
		return index;
	}
	
	// add commas to a number
	function add_commas(number) {
		var numtext = '' + number;
		var commas_text = '';
		for (i = numtext.length; i > 0; i -= 3)
			commas_text = (numtext.slice(Math.max(0, i - 3), i)
					+ (i < numtext.length ? ',' : '') + commas_text);
		return commas_text;
	}
	
	// divide by 100, fix to two decimal places and add dollar sign
	function format_currency(cents) {
		var dollars = (cents / 100).toFixed(2);
		return '$' + add_commas(dollars.slice(0, -3)) + dollars.slice(-3);
	}
	
	// load totals for each party and draw bars for each
	var party_totals = {};
	$.get('./results/totals.json', function(totals) {
		// get total for each party and year, and find the maximum
		var max = 1;
		$.each(totals, function(year, ydata) {
			$.each(ydata, function(party, pdata) {
				max = Math.max(max, pdata['sum_total']);
			});
		});
		
		$.each(sorted_index(totals).reverse(), function(i, year) {
			$('#years').append('<option>' + year + '</option>');
			$('#partyList').append('<div id="list-' + year + '">');
			
			// create colour bars for each party
			$.each(sorted_index(totals[year]), function(i, party) {
				$('#partyList #list-' + year).append(
					$('<a>' + party + '</a>').append($('<div>').css({
						width: '' + (totals[year][party]['sum_total'] / max * 100) + '%',
						backgroundColor: colours[party]
					}))
				);
			});
		});
		
		party_totals = totals;
		
		$('#years').trigger('change');
	});
	
	
	// load geographical results for each party and generate circles for each
	var party_circles = {};
	$.get('./results/postal_groups.json', function(pgroups) {
		var years = sorted_index(pgroups);
		
		// find largest single result and set scale accordingly
		var max = 1;
		$.each(years, function(i, year) {
			$.each(sorted_index(pgroups[year]), function(i, party) {
				$.each(pgroups[year][party], function(i, pgroup) {
					max = Math.max(max, Number(pgroup['Amount']));
				});
			});
		});
		
		var minSize = 20000;
		var scale = 2000000 / max;
		
		// generate circles for each party in each year
		$.each(years, function(i, year) {
			party_circles[year] = {};
			
			$.each(sorted_index(pgroups[year]), function(i, party) {
				party_circles[year][party] = [];
				var colour = colours[party];
				
				$.each(pgroups[year][party], function(i, pgroup) {
					var amount = Number(pgroup['Amount']);
					var radius = (minSize + amount) * scale / oldZoom;
					var circle = new google.maps.Circle({
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
					});
					var code = pgroup['Label']
					circle.set('code', pgroup['Label']);
					circle.set('count', pgroup['Count']);
					circle.set('amount', format_currency(amount));
					
					google.maps.event.addListener(circle, 'mouseover', function() {
						$('#codes').append(
							'<p id="code-' + this.code + '"><b>' + this.code + '</b> $' +
							this.amount + ' (' + this.count + ')</p>'
						);
					});
					google.maps.event.addListener(circle, 'mouseout', function() {
						$('#codes #code-' + this.code).remove();
					});

					party_circles[year][party].push(circle);
				});
			});
		});
	});
	
	
	// load data for this year, and select the same party if possible
	$('#years').change(function() {
		$('#info, #partyList > div').hide();
		clear_circles();
		
		var $yearlist = $('#partyList #list-' + $(this).val()).show();
		var party = $('#partyList a.selected').text();
		if (party)
			$yearlist.find('a:contains("' + party + '")').click();
	});
	
	
	// when party is clicked, show party info and circles
	$('#partyList').on('click', 'a', function(e) {
		e.preventDefault();
		
		if ($(this).hasClass('selected')) return;
		$('#partyList a').removeClass('selected');
		$(this).addClass('selected');
		
		var year = $('#years').val();
		var party = $(this).text();
		var colour = colours[party];
		
		// show info dialog for this party
		$('#info').show();
		$('#info h2').text($(this).text()).css('border-color', colour);
		$('#info .year').text(year);
		
		$('#info p').each(function() {
			var stat = $(this).attr('id');
			var amount = ($(this).hasClass('money')
					? format_currency(party_totals[year][party][stat])
					: add_commas(party_totals[year][party][stat]));
			$('.amount', $(this)).remove();
			$('<div class="amount">').text(amount).appendTo($(this));
		});
		$('#info .amount').css('color', colour);
		
		// clear existing circles and enable this party's circles
		clear_circles();
		circles = party_circles[year][party];
		$.each(circles, function(i, circle) {
			circle.setMap(map);
		});
	});
});
