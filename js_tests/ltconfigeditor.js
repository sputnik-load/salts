QUnit.test("LT Config Editor Test", function(assert) {
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
	var expected = {
		test_name: testData["test_name"],
		rps: testData["rps"],
		rampup: testData["rampup"] / 1000,
		testlen: testData["testlen"] / 1000,
		rampdown: testData["rampdown"] / 1000,
		target: testData["target"],
		port: testData["port"],
	};
	var binTestData = jsonstr2bin(JSON.stringify(testData));
	var htmlCode = "<a href='#' id='a' data-type='ltconfigeditor' " +
				   "data-value='" + binTestData + "' data-title='xyz'></a>";
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click();
	var p = e.data("editableContainer").tip();
	assert.ok(p.is(":visible"), "popover was visible");
	simpleTest = function(name, comment) {
		assert.equal(p.find("input[name=" + name + "]").val(),
					 expected[name], comment);	
	};
	simpleTest("test_name", "Test Name displays");
	simpleTest("rps", "RPS displays");
	simpleTest("rampup", "Ramp Up displays");
	simpleTest("rampdown", "Ramp Down displays");
	simpleTest("target", "Target displays");
	simpleTest("port", "Port displays");
	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		done();
	}, 300);
});
