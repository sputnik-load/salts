QUnit.test("Test 1", function(assert) {
	assert.ok(true, "Test 1 passes.");
	assert.ok(true, "Test 1 passes again.");
});


QUnit.test("Text Element Test From X-Editable", function(assert) {
	var done = assert.async();
	var htmlCode = "<a href='#' id='a' data-type='text' data-placeholder='abc' data-value='xyz'></a>";
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click();
	var p = e.data("editableContainer").tip();
	assert.ok(p.is(":visible"), "popover was visible");
	assert.equal(p.find("input[type=text]").attr("placeholder"), "abc", "placeholder exists");
	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		done();
	}, 300);
});


QUnit.test("SALTS: Custom Element Test", function(assert) {
	var done = assert.async();
	var testData = {
		test_name: "LT Config",
		rps: "5",
		rampup: "15000",
		testlen: "60000",
		rampdown: "10000",
		target: "xyz",
		port: "7654",
		s: "1"
	};
	var binTestData = jsonstr2bin(JSON.stringify(testData));
	var htmlCode = "<a href='#' id='a' data-type='customdata' " +
				   "data-value='" + binTestData + "' data-title='xyz'></a>";
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click();
	var p = e.data("editableContainer").tip();
	assert.ok(p.is(":visible"), "popover was visible");
	assert.equal(p.find("input[name=test_name]").val(), "LT Config", "Test Name displays");
	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		done();
	}, 300);
});
