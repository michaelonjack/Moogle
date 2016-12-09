
function exeSearch(q) {
	
	if (q.length > 0) {
		var xhttp = new XMLHttpRequest();

		xhttp.onreadystatechange = function() {
			
			if (xhttp.readyState == 4 && xhttp.status == 200) {
				
				var results = jQuery.parseJSON(xhttp.responseText);
				var dlist = jQuery('#json-list');
				dlist.empty();

				jQuery.each(results.data, function(k,v) {
					console.log(v.Name);
					dlist.append('<option value="' + v.Name + '">');
				});
			}
		};

		// TIMEOUT
		xhttp.ontimeout = function() {
			console.log("timeout");
		};

		xhttp.open("GET", "ajaxitemsearchresults?q=" + q, true);
		xhttp.timeout = 10000;
		xhttp.send();
	}
}

jQuery( document ).ready(function() {
	jQuery('#searchBar').on("keyup", function(e) {
		exeSearch( jQuery('#searchBar').val() );
	});
});