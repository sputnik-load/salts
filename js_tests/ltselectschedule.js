var gen = "phantom";


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
	var htmlCode = $.htmlCodeLTSelectSchedule("no", rps, gen);
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
	var expected = {
		view: [
			jsonstr2bin(JSON.stringify(initial)),
			jsonstr2bin(JSON.stringify(change))
		],
		opt_count: 3,
		a: [initial.params.a, change.params.a],
		dur: [ms2sec(initial.params.dur), ms2sec(change.params.dur)]
	};
	var htmlCode = $.htmlCodeLTSelectSchedule(initial.loadtype,
											  initial.params.a,
											  gen, initial.params);
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

	p.find("input[name=a]").val(change.params.a);
	p.find("input[name=dur]").val(ms2sec(change.params.dur));

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


QUnit.test("LT Select Schedule: Line Load", function(assert) {
	var done = assert.async();
	var initial = {
		loadtype: "line",
		params: {
			a: 5,
			b: 10,
			dur: 12000
		}
	};
	var change = {
		loadtype: "line",
		params: {
			a: 7,
			b: 14,
			dur: 20000
		}
	};
	var inp = {
		a: 7,
		b: 14,
		dur: 20
	};
	var expected = {
		view: [
			jsonstr2bin(JSON.stringify(initial)),
			jsonstr2bin(JSON.stringify(change))
		],
		opt_count: 3,
		a: [initial.params.a, change.params.a],
		b: [initial.params.b, change.params.b],
		dur: [ms2sec(initial.params.dur), ms2sec(change.params.dur)]
	};
	var htmlCode = $.htmlCodeLTSelectSchedule(initial.loadtype,
											  initial.params.a,
											  gen, initial.params);
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
	assert.equal(p.find("input[name=b]").val(), expected.b[0],
				 "The RPS value B from initial load schedule");
	assert.equal(p.find("input[name=dur]").val(), expected.dur[0],
				 "The duration value from initial load schedule");

	p.find("input[name=a]").val(change.params.a);
	p.find("input[name=b]").val(change.params.b);
	p.find("input[name=dur]").val(ms2sec(change.params.dur));

	p.find(".editable-submit").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		assert.equal(p.find("input[name=a]").val(), expected.a[1],
				     "New RPS value A saved");
		assert.equal(p.find("input[name=b]").val(), expected.b[1],
				     "New RPS value B saved");
		assert.equal(p.find("input[name=dur]").val(), expected.dur[1],
				     "New duration value saved");
		assert.equal(e.data("editable").value, expected.view[1],
					 "New value view: " + JSON.stringify(change));
		done();
	}, timeout);
});


QUnit.test("LT Select Schedule: Step Load", function(assert) {
	var done = assert.async();
	var initial = {
		loadtype: "step",
		params: {
			a: 5,
			b: 10,
			step: 2,
			dur: 12000
		}
	};
	var change = {
		loadtype: "step",
		params: {
			a: 7,
			b: 17,
			step: 3,
			dur: 8000
		}
	};
	var expected = {
		view: [
			jsonstr2bin(JSON.stringify(initial)),
			jsonstr2bin(JSON.stringify(change))
		],
		opt_count: 3,
		a: [initial.params.a, change.params.a],
		b: [initial.params.b, change.params.b],
		step: [initial.params.step, change.params.step],
		dur: [ms2sec(initial.params.dur), ms2sec(change.params.dur)]
	};
	var htmlCode = $.htmlCodeLTSelectSchedule(initial.loadtype,
											  initial.params.a,
											  gen, initial.params);
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
	assert.equal(p.find("input[name=b]").val(), expected.b[0],
				 "The RPS value B from initial load schedule");
	assert.equal(p.find("input[name=step]").val(), expected.step[0],
				 "The STEP value from initial load schedule");
	assert.equal(p.find("input[name=dur]").val(), expected.dur[0],
				 "The duration value from initial load schedule");

	p.find("input[name=a]").val(change.params.a);
	p.find("input[name=b]").val(change.params.b);
	p.find("input[name=step]").val(change.params.step);
	p.find("input[name=dur]").val(ms2sec(change.params.dur));

	p.find(".editable-submit").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		assert.equal(p.find("input[name=a]").val(), expected.a[1],
				     "New RPS value A saved");
		assert.equal(p.find("input[name=b]").val(), expected.b[1],
				     "New RPS value B saved");
		assert.equal(p.find("input[name=step]").val(), expected.step[1],
				     "New STEP value saved");
		assert.equal(p.find("input[name=dur]").val(), expected.dur[1],
				     "New duration value saved");
		assert.equal(e.data("editable").value, expected.view[1],
					 "New value view: " + JSON.stringify(change));
		done();
	}, timeout);
});


QUnit.test("LT Select Schedule: Jmeter Generator Type", function(assert) {
	var done = assert.async();
	var jmeter = "jmeter";
	var initial = {
		loadtype: "const",
		params: {
			a: 5,
			dur: 12000
		}
	};
	var htmlCode = $.htmlCodeLTSelectSchedule(initial.loadtype,
											  initial.params.a,
											  jmeter, initial.params);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click();
	var p = e.data("editableContainer").tip();
	assert.ok(p.is(":visible"), "popover was visible");

	var $schedule = p.find("div#select-schedule select#schedule");
	assert.ok($schedule.attr("disabled"), "Select Item is disabled.");

	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		done();
	}, timeout);
});
