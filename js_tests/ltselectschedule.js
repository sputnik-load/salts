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
