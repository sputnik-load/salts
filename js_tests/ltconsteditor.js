QUnit.test("LT Const Editor Test", function(assert) {
	var done = assert.async();
	var line = "constant for 100 rps for 00:10:00";
	var expected = {
		"title": "Constant Load For 100 rps",
		"value": "600"
	};
	var htmlCode = "<a href='#' id='a' data-type='ltconsteditor' " +
				   "data-value='" + line + "'></a>";
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click();
	var p = e.data("editableContainer").tip();
	assert.ok(p.is(":visible"), "popover was visible");
	assert.equal(p.find("input[name=testlen]").val(),
				 expected["value"], "Const Duration Length displays.");	
	assert.equal(p.find("input[name=testlen]").attr("title"),
				 expected["title"], "Window Title Test.");	
	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		done();
	}, 300);
});
