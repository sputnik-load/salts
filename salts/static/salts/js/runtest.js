var availTable			= $("#avail-table");
var runTable			= $("#run-table");
var MutationObserver    = window.MutationObserver ||
                          window.WebKitMutationObserver;
var myObserver          = new MutationObserver (mutationHandler);
var obsConfig           = {childList: true, characterData: true,
                           attributes: true, subtree: true };
var updateIntervalId;
var updateIntervalFunc;
var tanks;

function updateTestNameEditable(divItem) {
	var aItem = divItem.find('a');
	aItem.editable({
		showbuttons: 'bottom',
		value: bin2jsonstr(aItem.attr('data-value')),
		validate: function(value) {
			return;
		},
		display: function(value, sourceData) {
			if (aItem.attr('data-value') == value)
				return;
			if (!aItem.attr('data-old-value')) {
				aItem.attr('data-old-value', aItem.attr('data-value'));
			}
			aItem.attr('data-value', value);
			var dataOldValue = aItem.attr('data-old-value');
			if (dataOldValue && value == dataOldValue) {
				aItem.removeAttr('data-old-value');
				aItem.removeClass('editable-unsaved');
			}
			var data_value = JSON.parse(bin2jsonstr(aItem.attr('data-value')));
			aItem.text(data_value['test_name']);
			displayStartButton(divItem.parents('tr'));
		}
	});
}

function updateTankHostEditable(divItem) {
	var aItem = divItem.find('a');
	aItem.editable({
		display: function(value, sourceData) {
			var content = $.fn.editableutils.itemsByValue(value, sourceData);
			aItem.html(content[0]['text']);
			aItem.attr('data-value', value);
			displayStartButton(divItem.parents('tr'));
		}
	});
	aItem.editable('option', 'source', JSON.stringify(tanks['na']));
	aItem.editable('setValue', '-1', true);
	aItem.removeClass('editable-unsaved');
}

function updateRowIndexes() {
	var index = 0;
	availTable.filter("tr[data-index]").each(function() {
		$(this).attr("data-index", index);
		index += 1;
	});
}


function displayCustomData(customData) {
	var jsonStr = "";
    var htmlCode = "<ul>";
    if (customData != undefined)
    	jsonStr = bin2jsonstr(customData);
	else
    	jsonStr = "{}";
    $.each(JSON.parse(jsonStr), function(key, params) {
        htmlCode += "<li>" + key + "</li>";
        htmlCode += "<ul>";
        $.each(params, function(p, value) {
            htmlCode += "<li>" + p + ": " + value + "</li>";
        });
        htmlCode += "</ul>";
    });
    htmlCode += "</ul>";
    return htmlCode;
}

function displayTestNameCell(divItem) {
	if (divItem.find('a').size() > 0) {
		updateTestNameEditable(divItem);
	}
}

function updateScenarioStatus(scenarioRow, values) {
	var div = scenarioRow.find("div[name=status]");
	if (div.attr("update") == "false")
		return;
	var trId = parseInt(div.find('a').text());
	if ($.isEmptyObject(values) || trId == values['tr_id'])
		return;
	var testResultUrl = window.location.protocol + "//" +
						window.location.host +
						"/admin/salts/testresult/?id=" +
						values['tr_id'];
	var aContent = "<a href='" + testResultUrl + "' target='_blank'>" +
					values['tr_id'] + "</a>";
	var dateContent = "<p>" + moment.unix(values['finish']).format('YYYY-MM-DD HH:mm:ss') + "</p>";
	divContent = "Последний тест " + aContent + " был завершен " + dateContent;
	div.html(divContent);
}

function updateShootingStatus(shootingRow, values) {
	var statusContent = "Выполняется тест. ID сессии " + values['session'] +
						". Запущен " +
						moment.unix(values['start']).format('YYYY-MM-DD HH:mm:ss') +
						" пользователем <i>" + values['username'] + "</i>. ";
	statusContent += "Осталось - " + toHHMMSS(values['remained']) + ".";
	shootingRow.find('div[name=status]').html(statusContent);
	runTable.bootstrapTable("resetWidth");
}

function displayTankHostCell(divItem) {
	updateTankHostEditable(divItem);
	if (tanks['active']) {
		var trItem = divItem.parents('tr');
		var scenarioId = parseInt(trItem.find("td:eq(0)").text(), 10);
		$.each(tanks['active'], function(key, tank) {
			var shooting = tank['shooting'];
			if (scenarioId == shooting['scenario_id']) {
				var onclickHandler = "stopTest(" + shooting["scenario_id"] +
									 ", " + tank["id"] +
						 			 ", " + shooting["id"] + ")";
				var row = {
					shooting_id: shooting["id"],
					id: scenarioId,
					test_name: shooting["default_data"]["test_name"],
					tank_host: tank["text"],
					action_text: "Остановить",
					action_click_handler: onclickHandler,
					status: "",
					default_data: shooting["default_data"]
				};
				var trItems = runTable.find("tbody tr[data-index]");
				index = trItems.size();
				tr = runTable.find("tbody tr[data-uniqueid=" + shooting["id"] + "]");
				if (tr.size() === 0) {
					runTable.bootstrapTable("insertRow", {
						index: index,
						row: row
					});
					tr = runTable.find("tbody tr[data-uniqueid=" + shooting["id"] + "]");
					var butItem = tr.find("button");
					butItem.prop("disabled", !shooting["can_stop"]);
					var parentRunTable = runTable.parents("div.bootstrap-table");
					if (!parentRunTable.is(":visible")) {
						parentRunTable.show();
					}
					changeRunTableHeight();
				}
			}
		});
	}
}

function b64ScenarioChanges(aItem, custom_data) {
	if (aItem.size() == 0)
		return custom_data;
	if (!aItem.hasClass('editable-unsaved'))
		return custom_data;
	var initial = JSON.parse(bin2jsonstr(aItem.attr('data-old-value')));
	var current = JSON.parse(bin2jsonstr(aItem.attr('data-value')));
	var changes = {};
	$.each(current, function(name, value) {
		if (initial[name] != value) {
			changes[name] = value;
		}
	});
	return jsonstr2bin(JSON.stringify(changes));
}

function toScenarioFormat(aItem) {
	var gen_type = aItem.attr('data-gen-type');
	var data_value = JSON.parse(bin2jsonstr(aItem.attr('data-value')));
	var scenario = {
		sputnikreport: {
			test_name: data_value['test_name']
		}
	};
	var ms2sec = function(ms) { return ms / 1000; }
	if (gen_type == 'phantom') {
		scenario['phantom'] = {};
		scenario['phantom']['rps_schedule'] = "line(1," + data_value['rps'] +
			"," + ms2sec(data_value['rampup']) + "s) " +
			"const("+ data_value['rps'] + "," + ms2sec(data_value['testlen']) + "s) " +
			"line(" + data_value['rps'] + ",1," + ms2sec(data_value['rampdown']) + "s)";
		scenario['phantom']['address'] = data_value['target'] + ":" + data_value['port']
	}
	else {
		scenario['jmeter'] = {};
		scenario['jmeter']['rps1'] = data_value['rps'];
		scenario['jmeter']['rps2'] = data_value['rps'];
		scenario['jmeter']['rampup'] = ms2sec(data_value['rampup']);
		scenario['jmeter']['testlen'] = ms2sec(data_value['testlen']);
		scenario['jmeter']['rampdown'] = ms2sec(data_value['rampdown']);
		if (data_value['s']) {
			scenario['jmeter']['hostname'] = data_value['target'];
			scenario['jmeter']['port'] = data_value['port'];
		}
		else
			scenario['jmeter']['hostname'] = data_value['target'] + ":" +
											 data_value['port']
	}
	return jsonstr2bin(JSON.stringify(scenario));	
}


function displayStartButton(trItem) {
	var scenarioId = trItem.find("td:eq(0)").text();
	var onclickHandler = "";
	var butItem = trItem.find("button");
	var tankId = trItem.find("a[name='tank_host']").attr("data-value");
	disabled = true;
	if (tankId > 0) {
		disabled = false;
		var argsLine = scenarioId + ", " + tankId;
		argsLine += ", '" + toScenarioFormat(trItem.find("div[name='test_name'] a")) + "'";
		onclickHandler = "runTest(" + argsLine + ")";
	}
	butItem.prop("disabled", disabled);
	butItem.attr("onclick", onclickHandler);
	butItem.text("Запустить");
}

function mutationHandler(mutationRecords) {
	mutationRecords.forEach(function(mutation) {
		if (mutation.type == "childList") {
			$(mutation.addedNodes).each(function() {
				$(this).find("div[name='tank_host']").each(function() {
					var id = $(this).attr('id');
					displayTankHostCell($(this));
				});
				$(this).find("div[name='test_name']").each(function() {
					displayTestNameCell($(this));
				});
			});
		}
	});
}

function changeRunTableHeight() {
	var totalRows = runTable.bootstrapTable("getData").length;
	runTable.bootstrapTable("resetView",
							{"height": 150 * (totalRows + 1)});
}

function updateVisibleRows(scenBinStr) {
	$.ajax({
		type: 'get',
		url: '/run/',
		data: {'a': 1,
			   'b': scenBinStr},
		dataType: 'json',
		cache: false,
		success: function(upd) {
			setGlobalTanks(upd['tanks']);
			var trShootings = runTable.find("tbody tr[data-index]");
			var parentRunTable = runTable.parents("div.bootstrap-table");
			$.each(upd['rows'], function(k, info) {
				var div = $("div#scenario_" + info['id']);
				updateScenarioStatus(div.parents('tr'), info['last']);
			});
			var needUpdate = false;
			$.each(upd['tanks'], function(ix, js_str) {
				var shooting = JSON.parse(js_str)['shooting'];
				if (!$.isEmptyObject(shooting))	{
					var idSel = "[data-uniqueid=" + shooting["id"] + "]";
					if (!trShootings.is(idSel)) {
						displayTankHostCell(availTable.find("div#scenario_" + shooting['scenario_id']));	
						needUpdate = true;
					}
					else {
						updateShootingStatus(trShootings.filter(idSel),
											 shooting);
						trShootings = trShootings.not(idSel);
					}
				}
			});
			$(trShootings).each(function() {
				needUpdate = true;
				runTable.bootstrapTable("removeByUniqueId", $(this).attr("data-uniqueid"));
				changeRunTableHeight();
			});
			var trShootings = runTable.find("tbody tr[data-index]");
			if (trShootings.size() == 0)
				parentRunTable.hide();
			if (needUpdate)
				$("div[id^=scenario]").each(function() {
					displayTankHostCell($(this));
				});
		}
	});
}

function setGlobalTanks(t) {
	tanks = {na: [{value: "-1", text: "Не выбран"}],
				active: []};
	$.each(t, function(ix, js_str) {
		var tank = JSON.parse(js_str);
		if ($.isEmptyObject(tank['shooting'])) {
			tanks['na'].push({value: tank['value'],
								text: tank['text']});
		}
		else {
			tanks['active'].push(tank);
		}
	});

}

function ajax_request(params) {
	$.ajax(params).done(function(jsonObj) {
		setGlobalTanks(jsonObj['tanks']);
		updateIntervalFunc = function() {
			if (updateIntervalId)
				clearInterval(updateIntervalId);
			updateIntervalId = setInterval(function () {
				var scenarios = [];
				availTable.find('tr[data-index]').each(function() {
					scenarios.push(parseInt($(this).find('td:first').text(), 10));
				});
				updateVisibleRows(jsonstr2bin(JSON.stringify(scenarios)));
			}, 1000);
		}
		updateIntervalFunc();
	});
}

$(document).ready(function() {
	availTable.each(function() {
		myObserver.observe(this, obsConfig);
	});
	var parentRunTable = runTable.parents("div.bootstrap-table");
	parentRunTable.hide();
	$.fn.editable.defaults.mode = 'popup';
	$(document).on('visibilitychange', function() {
		if (document.visibilityState == 'hidden') {
			clearInterval(updateIntervalId);
			updateIntervalId = 0;
		}
		else {
			if (updateIntervalId == undefined)
				return;
			if (!updateIntervalId)
				updateIntervalFunc();
		}
	});
	$(window).resize(function() {
		availTable.bootstrapTable("resetView");
	});
});

function test_name_formatter(v, row, index) {
	var dataValue = jsonstr2bin(JSON.stringify(row['default_data']));
	var codeSelect = "<a href='#' id='test_name' " +
						"data-type='customdata' " +
						"data-gen-type='" + row['default_data']['gen_type'] + "' " +
						"data-placement='right' " +
						"data-value='" + dataValue + "'" +
						"data-title='Изменяемые параметры'>" +
						row['test_name'] + "</a>";
	return "<div name='test_name'>" + codeSelect + "</div>" +
				"<div name='custom_data' " +
				"style='font-family:courier;font-size:70%'></div>";
}

function availTankHostFormatter(v, row, index) {
	var codeSelect = "<a href='#' name='tank_host'" +
						"data-source='' " +
						"data-type='select' data-value='' " +
						"data-placement='right' " +
						"data-title='Имя хоста с танком'></a>";
	return "<div name='tank_host' id='scenario_" + row['id'] + "'>" +
			codeSelect + "</div>";
}

function getErrorMessage(failures) {
	var preamble = "Тест не смог быть запущен по причине:<br>";
	var content = "";
    $.each(failures, function(ix, item) {
		if (item["reason"] === "skipped")
			return true;
		if (item["stage"] !== "prepare")
			preamble = "Тест был некорректно завершен по причине: ";
		$.each(item["reason"].split("\n"), function(kx, line) {
			if (line)
				content += line + "<br>";
		});
		return false;
	});
	return preamble + "<span style='color:red;'>" + content + "</span>";
}

function runTest(scenario_id, tank_id, b64line) {
	var $row = $("div[id='scenario_" + scenario_id + "']").parents("tr");
	var $button = $row.find("button");
	$button.attr("disabled", true);
	var data_url = "/shoot/?s=" + scenario_id + "&t=" + tank_id;
	if (b64line) {
		data_url += "&j=" + b64line;
	}

	$.ajax({
		url: data_url,
		type: 'GET',
		dataType: 'json',
		success: function(resp) {
			var $div = $row.find("div[name=status]");
			$div.attr("update", "true");
		},
		error: function(resp) {
			var jsonObj = JSON.parse(resp["responseText"]);
			var $div = $row.find("div[name=status]");
			$div.attr("update", "false");
			$button.attr("disabled", false);
			$div.html(getErrorMessage(jsonObj["failures"]));
			availTable.bootstrapTable("resetView");
		}
	});
}

function stopTest(scenario_id, tank_id, shooting_id) {
	var trItem = $("div[id='shooting_" + shooting_id + "']").parents('tr');
	trItem.find('button').attr('disabled', true);
	var data_url = "/shoot/?stop=" + shooting_id;
	var resp = $.ajax({
		url: data_url,
		type: 'GET',
		dataType: 'json',
		success: function(json) {
		},
		error: function(json) {
			console.log("Response: " + JSON.stringify(json));
		}
	});
}

function action_formatter(v, row, index) {
	return "<button type='button' class='btn btn-primary' " +
		   "id='action_btn' " + "onclick='" +
			row["action_click_handler"] + "'>" +
			row["action_text"] + "</button>";
}

function statusFormatter(v, row, index) {
	return "<div name='status' update='true'><a></a>Нет результатов</div>";
}
