var testData = {
	test_name: "LT Config",
	rps: 5,
	rampup: 15000,
	testlen: 60000,
	load: {"const": 60000,
		   "step" : [10, 2, 10000]},
	rampdown: 10000,
	target: "xyz",
	port: 7654,
	s: 1
};

var expected = {
	test_name: testData.test_name,
	rps: testData.rps,
	rampup: testData.rampup / 1000,
	testlen: testData.testlen / 1000,
	rampdown: testData.rampdown / 1000,
	target: testData.target,
	port: testData.port,
};

var timeout = 300;


QUnit.test("LT Config Editor: No User Load", function(assert) {
	var done = assert.async();
	var binTestData = jsonstr2bin(JSON.stringify(testData));
	var htmlCode = "<a href=# id=a data-type=ltconfigeditor " +
				   "data-value='" + binTestData + "' data-title=xyz></a>";
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
	var $load = p.find("div#load");
	var $select = $load.find("a");
	assert.equal($select.text(), "Select To Add New Scheme",
				 "new user load: the initial value of rps is correct");
	assert.equal($select.attr("data-rps"), testData.rps,
				 "new user load: value view");
	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		done();
	}, timeout);
});


QUnit.test("LT Config Editor: the 'Add/Remove' Button", function(assert) {
	var done = assert.async();
	var binTestData = jsonstr2bin(JSON.stringify(testData));
	var htmlCode = "<a href=# id=a data-type=ltconfigeditor " +
				   "data-value='" + binTestData + "' data-title=xyz></a>";

	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click(); // to open configeditor

	var p = e.data("editableContainer").tip();
	var $load = p.find("div#load tr");
	assert.equal($load.size(), 1, "the load items' count is 1 after click on the 'Plus' button");
	var $button = $load.find("button");
	assert.ok($button.is(".btn-plus"), "the 'Plus' button shown");
	assert.ok($button.attr("disabled"), "the 'Plus' button must be disabled");

	var $select = $load.find("a");
	$select.click(); // to open ltscheduleselect

	var $selectEditable = $select.data("editableContainer").tip();
	$selectEditable.find("select").val("const"); // select const schedule

	// to confirm selection and close ltselectschedule
	$selectEditable.find(".editable-submit").click();

	$button = $load.find("button");
	assert.ok(!$button.attr("disabled"), "the 'Plus' button must be enabled");

	$select.click(); // to open ltselectschedule
	$selectEditable = $select.data("editableContainer").tip();
	var $opt = $selectEditable.find("#schedule option");
	assert.equal($opt.size(), 2, "the options' count is 2 after selection");

	// to close ltselectschedule without change
	$selectEditable.find(".editable-cancel").click();


	$button = $load.find("button");
	$button.click(); // to add current schedule

	$load = p.find("div#load tr");
	assert.equal($load.size(), 2, "the load items' count is 2 after click on the 'Plus' button");
	assert.ok($button.hasClass("btn-sm"), "the 'Remove' button shown");

	// $button = $load.find("button");
	$button.click(); // to remove corresponding row
	$load = p.find("div#load tr");
	assert.equal($load.size(), 1, "the load items' count is 1 after click on the 'Remove' button");

	p.find(".editable-cancel").click();
	setTimeout(function() {
		done();
	}, timeout);
});
