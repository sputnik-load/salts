QUnit.test("LT Const Editor Test", function(assert) {
	var done = assert.async();
	var rps = 100;
	var duration = 600; // seconds
	var expected = {
		"line": "constant for 100 rps for 00:10:00",
		"title": "Constant Load For 100 rps",
		"value": "600"
	};
	var htmlCode = htmlCodeLTConstEditor("abc", 100, 600);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click();
	var p = e.data("editableContainer").tip();
	assert.ok(p.is(":visible"), "popover was visible");
	assert.equal(p.find("input[name=testlen]").val(),
				 expected["value"], "Const Duration Test.");
	assert.equal(p.find(".popover-title").text(),
				 expected["title"], "Window Title Test.");	
	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		done();
	}, 300);
});
