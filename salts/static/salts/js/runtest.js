var targetNodes         = $("#table");
var MutationObserver    = window.MutationObserver ||
                            window.WebKitMutationObserver;
var myObserver          = new MutationObserver (mutationHandler);
var obsConfig           = {childList: true, characterData: true,
                            attributes: true, subtree: true };
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
			var jsonObj = JSON.parse(bin2jsonstr(aItem.attr('data-value')));
			aItem.text(jsonObj['sputnikreport']['test_name']);
			displayActionButton(divItem.parents('tr'));
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
			displayActionButton(divItem.parents('tr'));
		}
	});
	aItem.editable('option', 'source', JSON.stringify(tanks['na']));
	aItem.editable('setValue', '-1', true);
	aItem.removeClass('editable-unsaved');
}

function updateRowIndexes() {
	var index = 0;
	$("#table tr[data-index]").each(function() {
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
						". Запущен " + moment.unix(values['start']).format('YYYY-MM-DD HH:mm:ss') + ". ";
	var duration = parseInt(values['duration'], 10);
	if (duration !== undefined && duration > 0) {
		var d = new Date();
		var currentTime = parseInt(d.getTime() / 1000);
		statusContent += "Осталось - " + toHHMMSS(duration - (currentTime - values['start'])) + ".";
	}
	shootingRow.find('div[name=status]').html(statusContent);
}

function displayTankHostCell(divItem) {
	var idValue = divItem.attr('id').replace(/_\d+/, '');
	if (idValue == "shooting") {
		displayActionButton(divItem.parents('tr'));
		return;
	}
	updateTankHostEditable(divItem);
	if (tanks['active']) {
		var scenarioId = parseInt(divItem.attr('id').replace(/scenario_/, ''),
								  10);
		$.each(tanks['active'], function(key, tank) {
			var shooting = tank['shooting'];
			if (scenarioId == shooting['scenario_id']) {
				var trItem = divItem.parents('tr');
				var newItem = trItem.clone();
				var newDiv = newItem.find("div[id='scenario_" + scenarioId + "']");
				newDiv.attr('id', "shooting_" + shooting['id']);
				newDiv.html("<p value='" + tank['value'] +
							"'>" + tank['text'] + "</p>");
				newDiv = newItem.find("div[name='custom_data']");
				newDiv.html("<span>" +
							displayCustomData(b64ScenarioChanges(trItem.find("div[name='test_name'] a"))) +
							"</span>");
				newDiv = newItem.find("div[name='test_name']");
				newDiv.html("<p>" + shooting['default_data']['sputnikreport']['test_name'] + ":</p>");
				newItem.insertBefore(trItem);
				updateShootingStatus(newItem, shooting);
			}
		});
	}
}

function b64ScenarioChanges(aItem) {
	if (!aItem.hasClass('editable-unsaved'))
		return;
	var initial = JSON.parse(bin2jsonstr(aItem.attr('data-old-value')));
	var current = JSON.parse(bin2jsonstr(aItem.attr('data-value')));
	var changes = {};
	$.each(current, function(section, params) {
		$.each(params, function(name, value) {
			if (initial[section][name] != value) {
				if (!changes.hasOwnProperty(section)) {
					changes[section] = {};
				}
				changes[section][name] = value;
			}
		});
	});
	return jsonstr2bin(JSON.stringify(changes));
}

function displayActionButton(trItem) {
	var scenarioId = trItem.find('td:eq(0)').text();
	var shootingId = parseInt(trItem.find("div[name='tank_host']")
								.attr('id').replace(/shooting_/, ''), 10);
	var onclickHandler = '';
	var butItem = trItem.find('button');
	var butName = "Запустить";
	var disabled = true;
	if (shootingId) {
		disabled = false;
		var tankId = trItem.find('p[value]').attr('value');
		onclickHandler = "stopTest(" + scenarioId + ", " + tankId +
							", " + shootingId + ")";
		butName = "Остановить";
	}
	else {
		var tankId = trItem.find("a[name='tank_host']").attr('data-value');
		if (tankId > 0) {
			disabled = false;
			var argsLine = scenarioId + ", " + tankId;
			var b64Line = b64ScenarioChanges(trItem.find("div[name='test_name'] a"));
			if (b64Line) {
				argsLine += ", '" + b64Line + "'";
			}
			onclickHandler = "runTest(" + argsLine + ")";
		}
	}
	butItem.prop('disabled', disabled);
	butItem.attr('onclick', onclickHandler);
	butItem.text(butName);
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
			var divShootings = $("div[id^=shooting]");
			$.each(upd['rows'], function(k, info) {
				var div = $("div#scenario_" + info['id']);
				updateScenarioStatus(div.parents('tr'), info['last']);
			});
			var needUpdate = false;
			$.each(upd['tanks'], function(ix, js_str) {
				var shooting = JSON.parse(js_str)['shooting'];
				if (!$.isEmptyObject(shooting))	{
					var idSelector = "[id=shooting_" + shooting['id'] + "]";
					if (!divShootings.is(idSelector)) {
						displayTankHostCell($("div#scenario_" + shooting['scenario_id']));
						needUpdate = true;
					}
					else {
						updateShootingStatus(divShootings.filter(idSelector).parents('tr'),
											 shooting);
						divShootings = divShootings.not(idSelector);
					}
				}
			});
			$(divShootings).each(function() {
				needUpdate = true;
				$(this).parents('tr').remove();
				$("div[id^=scenario]").each(function() {
					displayTankHostCell($(this));
				});
			});
			if (needUpdate)
				updateRowIndexes();
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
		var scenarios = [];
		$('table#table tr[data-index]').each(function() {
			scenarios.push(parseInt($(this).find('td:first').text(), 10));
		});
		setInterval(function () {
			updateVisibleRows(jsonstr2bin(JSON.stringify(scenarios)));
		}, 1000);
	});
}

$(document).ready(function() {
	targetNodes.each(function() {
		myObserver.observe(this, obsConfig);
	});
	$.fn.editable.defaults.mode = 'popup';
});

function test_name_formatter(v, row, index) {
	var dataValue = jsonstr2bin(JSON.stringify(row['default_data']));
	var codeSelect = "<a href='#' id='test_name' " +
						"data-type='customdata' " +
						"data-placement='right' " +
						"data-value='" + dataValue + "'" +
						"data-title='Изменяемые параметры'>" +
						row['test_name'] + "</a>";
	return "<div name='test_name'>" + codeSelect + "</div>" +
				"<div name='custom_data' " +
				"style='font-family:courier;font-size:70%'></div>";
}

function tank_host_formatter(v, row, index) {
	var codeSelect = "<a href='#' name='tank_host'" +
						"data-source='' " +
						"data-type='select' data-value='' " +
						"data-placement='right' " +
						"data-title='Имя хоста с танком'></a>";
	return "<div name='tank_host' id='scenario_" + row['id'] + "'>" +
			codeSelect + "</div>";
}

function runTest(scenario_id, tank_id, b64line) {
	$("div[id='scenario_" + scenario_id + "']").parents('tr')
		.find('button').attr('disabled', true);
	var data_url = "/shoot/?s=" + scenario_id + "&t=" + tank_id;
	if (b64line) {
		data_url += "&j=" + b64line;
	}

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
		   "id='action_btn' " + "onclick=''></button>";
}

function statusFormatter(v, row, index) {
	return "<div name='status'><a></a>Нет результатов</div>";
}
