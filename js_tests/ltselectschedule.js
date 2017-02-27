QUnit.test("LT Select Schedule: New Schedule Without Change", function(assert) {
	var done = assert.async();
	var timeout = 300;
	var rps = 100;
	var expectedValue = {
		loadtype: "no",
		params: {}
	};
	var expected = {
		view: jsonstr2bin(JSON.stringify(expectedValue)),
		title: "Set the load profile",
		opt_count: 4
	};
	var htmlCode = $.htmlCodeLTSelectSchedule("no", rps);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	assert.equal(e.data("editable").value,
				 expected.view,
				 "value view before popover");
	e.click();
	var p = e.data("editableContainer").tip();
	assert.ok(p.is(":visible"), "popover was visible");
	var options = p.find("div#select-schedule select#schedule").find("option");
	assert.equal(options.length, expected.opt_count,
				 "Options Count is " + expected.opt_count + ".");
	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		assert.equal(e.data("editable").value,
					 expected.view, "value view after cancel");
		e.click();
		p = e.data("editableContainer").tip();
		p.find(".editable-submit").click();
		setTimeout(function() {
			assert.equal(e.data("editable").value,
						 expected.view, "value view after submit");
			done();
		}, timeout);
	}, timeout);
});


QUnit.test("LT Select Schedule: Const Load", function(assert) {
	var done = assert.async();
	var initial = {
		loadtype: "const",
		params: {
			a: 5,
			dur: 12000
		}
	};
	var change = {
		loadtype: "const",
		params: {
			a: 7,
			dur: 15000
		}
	};
	var inp = {
		a: 7,
		dur: 15
	};
	var expected = {
		view: [
			jsonstr2bin(JSON.stringify(initial)),
			jsonstr2bin(JSON.stringify(change))
		],
		opt_count: 3,
		a: [5, 7],
		dur: [12, 15],
	};
	var htmlCode = $.htmlCodeLTSelectSchedule(initial.loadtype, initial.params.a, initial.params);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	assert.equal(e.data("editable").value, expected.view[0],
				 "Value view before popover: " + JSON.stringify(initial));
	e.click();
	var p = e.data("editableContainer").tip();
	assert.ok(p.is(":visible"), "popover was visible");

	var options = p.find("div#select-schedule select#schedule").find("option");
	assert.equal(options.length, expected.opt_count,
				 "Options Count is " + expected.opt_count + ".");

	assert.equal(p.find("input[name=a]").val(), expected.a[0],
				 "The RPS value A from initial load schedule");

	assert.equal(p.find("input[name=dur]").val(), expected.dur[0],
				 "The duration value from initial load schedule");

	p.find("input[name=a]").val(inp.a);
	p.find("input[name=dur]").val(inp.dur);

	p.find(".editable-submit").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		assert.equal(p.find("input[name=a]").val(), expected.a[1],
				     "New RPS value A saved");
		assert.equal(p.find("input[name=dur]").val(), expected.dur[1],
				     "New duration value saved");
		assert.equal(e.data("editable").value, expected.view[1],
					 "New value view: " + JSON.stringify(change));
		done();
	}, timeout);

});
