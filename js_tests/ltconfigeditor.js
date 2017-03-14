var testData = {
	test_name: "LT Config",
	gen_type: "phantom",
	steps: [{loadtype: "line", params: {a: 1, b: 5, dur: 15000}},
		    {loadtype: "const", params: {a: 5, dur: 60000}},
		    {loadtype: "line", params: {a: 5, b: 1, dur: 10000}}],
	hostname: "xyz",
	port: 7654,
	s: 1
};
var inp = {
	id: 1,
	data: testData,
	title: "Config Title",
	text: "Config Editor"
};

var isParamsValidAndEqual = function(a, b) {
	var keys = ["test_name", "steps", "hostname", "port", "s"];
	var stepKeys = ["loadtype", "params"];
	for (var i = 0; i < keys.length; i++) {
		var k = keys[i];
		if ( !(k in a) || !(k in b) )
			return 1;
		if (k == "steps") {
			if (a.steps.length != b.steps.length)
				return 2;
			for (var j = 0; j < a.steps.length; j++) {
				var sk = "loadtype";
				if ( !(sk in a.steps[j]) || !(sk in b.steps[j]) )
					return 3;
				if ( a.steps[j][sk] != b.steps[j][sk] )
					return 4;
				sk = "params";
				if ( !(sk in a.steps[j]) || !(sk in b.steps[j]) )
					return 5;
				for (var p in a.steps[j].params) {
					if ( !(p in b.steps[j].params) )
						return 6;
					if ( a.steps[j].params[p] != b.steps[j].params[p] )
						return 7;
				}
			}
		}
	}
	return 0;
}

var timeout = 300;


QUnit.test("LT Config Editor: No User Load", function(assert) {
	var expectedData = {
		test_name: testData.test_name,
		rps: testData.rps,
		hostname: testData.hostname,
		port: testData.port,
	};
	var done = assert.async();
	var htmlCode = $.htmlCodeLTConfigEditor(inp.id, inp.title,
											inp.data, inp.text);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click();
	var p = e.data("editableContainer").tip();

	assert.ok(p.is(":visible"), "popover was visible");
	simpleTest = function(name, comment) {
		assert.equal(p.find("input[name=" + name + "]").val(),
					 expectedData[name], comment);
	};
	simpleTest("test_name", "Test Name displays");
	simpleTest("hostname", "Target displays");
	simpleTest("port", "Port displays");

	var $load = p.find("div#load a");
	assert.equal($load.size(), 3, "The count of load schedules is 3");
	assert.equal($load[0].text, "линейная нагрузка от 1 до 5 rps",
				 "Rampup line load.");
	assert.equal($load[1].text, "постоянная нагрузка 5 rps",
				 "Const line load.");
	assert.equal($load[2].text, "линейная нагрузка от 5 до 1 rps",
				 "Rampdown line load.");
	assert.equal($($load[0]).attr("data-rps"), 1,
				 "base rps");
	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		done();
	}, timeout);
});


QUnit.test("LT Config Editor: the 'Add' Button", function(assert) {
	var expectedData = {
		test_name: "LT Config",
		steps: [{loadtype: "line", params: {a: 1, b: 5, dur: 15000}},
				{loadtype: "step", params: {a: 4, b: 20, step: 4, dur: 4000}},
				{loadtype: "const", params: {a: 5, dur: 60000}},
				{loadtype: "line", params: {a: 5, b: 1, dur: 10000}}],
		hostname: "xyz",
		port: 7654,
		s: 1
	};

	var done = assert.async();
	var htmlCode = $.htmlCodeLTConfigEditor(inp.id, inp.title,
											inp.data, inp.text);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click(); // to open configeditor

	var p = e.data("editableContainer").tip();
	var $load = $(p.find("div#load div.row")[0]);
	var $addbut = $load.find("button[name=add]");
	assert.ok($addbut.is(".btn-plus"), "the 'Plus' button shown");
	assert.ok(!$addbut.prop("disabled"), "the 'Plus' button is enabled");

	var $delbut = $load.find("button[name=del]");
	assert.ok($delbut.is(".btn-sm"), "the 'Delete' button shown");
	assert.ok(!$delbut.prop("disabled"), "the 'Delete' button is enabled");

	$addbut.click();
	$load = p.find("div#load div.row");
	assert.equal($load.size(), 4, "the row count was incremented, now 4");

	var $aNewLoad = $($load.get(1)).find("a");
	assert.equal($aNewLoad.text(), "добавить новую схему нагрузки",
				 "New Load Item text value");
	$aNewLoad.click(); // to open load schedule editor

	var $loadEditable = $aNewLoad.data("editableContainer").tip();
	var $select = $loadEditable.find("select#schedule");
	assert.equal($select.size(), 1, "Select Item was obtained.");
	assert.equal($select.val(), "no", "No Items are selected.");
	$select.val("step");
	$select.trigger("change");
	assert.equal($select.val(), "step", "Step Option are selected.");

	var $inputs = $loadEditable.find("div#param input");
	$inputs.filter("[name=a]").val("4");
	$inputs.filter("[name=b]").val("20");
	$inputs.filter("[name=step]").val("4");
	$inputs.filter("[name=dur]").val("4");
	$loadEditable.find(".editable-submit").click();

	assert.equal($aNewLoad.text(), "ступенчатая нагрузка от 4 до 20 rps",
				 "New Stepped Load text value");

	p.find(".editable-submit").click();
	setTimeout(function() {
		var binData = e.editable("getValue", true);
		var decodeData = JSON.parse(bin2jsonstr(binData));
		assert.equal(isParamsValidAndEqual(expectedData, decodeData), 0,
					 "The changes are corrected");
		done();
	}, timeout);
});


QUnit.test("LT Config Editor: the 'Delete' Button", function(assert) {
	var expectedData = {
		test_name: "LT Config",
		steps: [{loadtype: "line", params: {a: 1, b: 5, dur: 15000}},
				{loadtype: "line", params: {a: 5, b: 1, dur: 10000}}],
		hostname: "xyz",
		port: 7654,
		s: 1
	};

	var done = assert.async();
	var htmlCode = $.htmlCodeLTConfigEditor(inp.id, inp.title,
											inp.data, inp.text);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click(); // to open configeditor

	var p = e.data("editableContainer").tip();
	var $load = $(p.find("div#load div.row")[1]);
	var $delbut = $load.find("button[name=del]");
	assert.ok($delbut.is(".btn-sm"), "the 'Delete' button shown");
	assert.ok(!$delbut.prop("disabled"), "the 'Delete' button is enabled");

	var $delbut = $load.find("button[name=del]");
	assert.ok($delbut.is(".btn-sm"), "the 'Delete' button shown");
	assert.ok(!$delbut.prop("disabled"), "the 'Delete' button is enabled");

	$delbut.click();
	$load = p.find("div#load div.row");
	assert.equal($load.size(), 2, "the row count was decremented, now 2");

	p.find(".editable-submit").click();
	setTimeout(function() {
		var binData = e.editable("getValue", true);
		var decodeData = JSON.parse(bin2jsonstr(binData));
		assert.equal(isParamsValidAndEqual(expectedData, decodeData), 0,
					 "The changes are corrected");
		done();
	}, timeout);
});


QUnit.test("LT Config Editor: JMeter Generator Type", function(assert) {
	var done = assert.async();
	inp.data.gen_type = "jmeter";
	var htmlCode = $.htmlCodeLTConfigEditor(inp.id, inp.title,
											inp.data, inp.text);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click(); // to open configeditor

	var p = e.data("editableContainer").tip();
	$.each(p.find("div#load"), function() {
		assert.ok($(this).find("button[name=add]").prop("disabled"),
				  "The 'Add' button disabled");
		assert.ok($(this).find("button[name=del]").prop("disabled"),
				  "The 'Del' button disabled");
	});
	p.find(".editable-cancel").click();
	setTimeout(function() {
		done();
	}, timeout);
});
