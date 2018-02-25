var get_args = location.search;
var a = document.createElement('a');
var linkText = document.createTextNode(Lang.tr.results_page.dynamics.link);
a.appendChild(linkText);
a.title = Lang.tr.results_page.dynamics.title;
a.href = "/results/graph/" + get_args;    
var parent = document.getElementById("linker");      
parent.appendChild(a);            
var $table = $('.table');

$(document).ready(function() {
	menuChangeLocale();
	$("title").text("SALTS: " + Lang.tr.results_page.title);
	var $toolbar = $("div#results-table-toolbar");
	$toolbar.find("h3").text(Lang.tr.results_page.table.title);
	$toolbar.find("a[name=help]").text(Lang.tr.results_page.help);
	var $tbl = $("#results-bs-tbl");
	$tbl.bootstrapTable("changeLocale", Lang.current);
	$tbl.bootstrapTable("changeTitle", Lang.tr.results_page.table.columns);
});

function edit_page_url(edit_url, id) {
	return window.location.protocol + "//" +
		   window.location.host + edit_url + id;
}

function ajax_request(params) {
	var url_param = $.url().param();
	for (name in url_param) {
		if (!params.data.hasOwnProperty(name)) {
			params.data[name] = url_param[name];
		}
	}
	if ('cc' in url_param && url_param['cc'] === '0') {
		params.cache = false;
  	}
	$.ajax(params);        
}

function graph_url_formatter(value) {
	if (value === "") {
    	return "-";
	}
	var aItem = "<a href='{link}'>{desc}</a>";
	aItem = aItem.replace("{link}", value);
	aItem = aItem.replace("{desc}", Lang.tr.results_page.table.columns.graph_url);
	return aItem;
}

function ticket_id_formatter(value) {
	if (value === "") {
    	return "-";
	}
	return "<a href='https://<JIRA_URL>/browse/" + value +
		   "' target='_blank'>" + value + "</a>";
}

function test_name_formatter(value, row) {
	if (value === '') {
		return '-';
	}
	if (row['edit_url'] === '') {
		return value;
	}
	return "<a href='" + edit_page_url(row['edit_url'], row['id']) +
		   "'>" + value + "</a>";
}

function test_status_formatter(value, row) {
	var human_values = {
		unk: "Unknown",
		dbg: "Debug",
		pass: "Pass",
		fail: "Fail"
	};
	return human_values[value];
}

function row_style(row, index) {
	var css_status_classes = { 
		unk: "unk", 
		dbg: "debug",
		fail: "failed",
		pass: "success"
	};
	if (index % 2 === 0) {	
		clsline = css_status_classes[row["test_status"]] + "_even";
	}
	else
		clsline = css_status_classes[row["test_status"]] + "_odd";
	clsline += " lt-cell";
	return {classes: clsline};
}

$('#results-bs-tbl').bootstrapTable({
	onDblClickRow: function (row, $element) {
		if (row['edit_url'] === '') {
			return;
		}
		window.open(edit_page_url(row['edit_url'], row['id']));
	}
});
