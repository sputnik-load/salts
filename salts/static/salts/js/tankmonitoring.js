$(document).ready(function() {
	menuChangeLocale();
	$("title").text("SALTS: " + Lang.tr.tanks_page.title);
	$("div#monitoring-table-toolbar h3").text(Lang.tr.tanks_page.table.title);
	var $tbl = $("#table");
	$tbl.bootstrapTable("changeLocale", Lang.current);
	$tbl.bootstrapTable("changeTitle", Lang.tr.tanks_page.table.columns);
});

function ajax_request(params) {
	var resp = $.ajax(params);       
}

function status_formatter(st) {
	var choices = Lang.tr.tanks_page.status.choices;
	var status_values = {
		"P": choices.starting,
		"R": choices.running,
		"I": choices.interrupted,
		"F": choices.finished
	}
	return status_values[st];
}

function countdown_formatter(v, row, index) {
	if (v === -1) {
		return "Не определено"
	}
	return remainedTime(v, row, index);
}

function webconsole_formatter(v, row, index) {
	if (v === undefined) {
		return "-";
	}
	return "<a href='http://" + v + "' target='_blank'>" + v + "</a>";
}

function scenario_name_formatter(v, row, index) {
	if (v === undefined) {
		return "-";
	}
	return "<a href='" + row['gitlab_url'] + "' target='_blank'>" + 
		   row['scenario_name'] + "</a>";
}

function test_result_formatter(v, row, index) {
	if (v === undefined) {
		return "-";
	}

	var test_result_url = window.location.protocol + "//" +
						  window.location.host +
						  "/admin/salts/testresult/?id=" + v;
	return "<a href='" + test_result_url + "' target='_blank'>" +
		   row['test_result'] + "</a>";
}

function ticket_url_formatter(v, row, index) {
	if (v === undefined) {
		return "-";
	}
	return "<a href='" + row['ticket_url'] + 
			"' target='_blank'>" + row['ticket_id'] + "</a>";
}

function remainedTime(sec_num, row, index, n) {
	if (n === undefined) {
		n = 0;
	}
	if (sec_num < 0)
		sec_num = 0;

	var time_line = toHHMMSS(sec_num);

	var td = $("#table tbody tr:nth-child(" + (index+1) + ") td");
	var th = $("#table thead th");

	if ($(td).size() > 1) {
		var ix = $(th).filter("[data-field='status']").index();
		if (ix != -1) 
			$(td).eq(ix).html(status_formatter(row['status']));
		ix = $(th).filter("[data-field='countdown']").index();
		if (ix != -1) {
			$(td).eq(ix).html(time_line);
		}
		if (row['status'] == 'R')
			sec_num -= 0.5;
		if ($.inArray(row['status'], ['I', 'F']) >= 0)
			return time_line;
	} 
	if (n > 0 && !(n % 10)) {
		$.ajax({
			url: "/get_tank_status/?tank_id=" + row['id'],
			type: "GET",
			dataType: "json",
			data: {},
			error: function(json) {},
			success: function(json) {
				resp = json['rows'][0];
				sec_num = resp['countdown'];
				row['status'] = resp['status'];
				remainedTime(sec_num, row, index, n+1)
			}
		});
	}
	else {
		setTimeout(function () {
			remainedTime(sec_num, row, index, n+1)
		}, 500);
	}
	return time_line;
}

function row_style(row, index) {
	var clsline = "";
	/*
	  if (index % 2 === 0) {	
		clsline = css_status_classes[row["test_status"]] + "_even";
	  }
	  else
		clsline = css_status_classes[row["test_status"]] + "_odd";
	*/
	clsline += " lt-cell";
	return {classes: clsline};
}
