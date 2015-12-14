function pagination_hide() {
	var vars = {};
    var x = document.location.search.substring(1).split('&');
    for (var i in x) {
        var z = x[i].split('=', 2);
        vars[z[0]] = unescape(z[1]);
    }
    var x=['frompage', 'topage', 'page', 'webpage', 'section', 'subsection', 'subsubsection'];
    for (var i in x) {
        var y = document.getElementsByClassName(x[i]);
        for (var j=0; j<y.length; ++j)
            y[j].textContent = vars[x[i]];
    }
    
    // not-first-page: shows element in every page but first
    // not-last-page: shows element in every page but last
    // first-page: shows element only on first page
    // last-page: shows element only on last page

    var operations = {
    	'not-first-page': function (elt) {
            elt.style.visibility = (vars.page === vars.frompage) ? "hidden" : "visible";
        },
        'not-last-page': function (elt) {
            elt.style.visibility = (vars.page === vars.topage) ? "hidden" : "visible";
        },
        'first-page': function (elt) {
            elt.style.visibility = (vars.page === vars.frompage) ? "visible" : "hidden";
        },
        'last-page': function (elt) {
            elt.style.visibility = (vars.page === vars.topage) ? "visible" : "hidden";
        },
        'spacer': function (elt) {
        	elt.style.visibility = (vars.page === vars.topage) ? "hidden" : "visible";
        }
    };

    for (var klass in operations) {
        var y = document.getElementsByClassName(klass);
        for (var j=0; j<y.length; ++j)
            operations[klass](y[j]);
    }
}