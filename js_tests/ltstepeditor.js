QUnit.test("LT Step Editor Cancel Test", function(assert) {
	var done = assert.async();
	var start = 25;
	var finish = 5;
	var step = 5;
	var duration = 600; // seconds
	var expected = {
		"view": "stepped from 25 to 5 rps, with 5 rps steps, step duration 00:10:00",
		"title": "Stepped Load From 25 RPS",
		"value": "600"
	};
	var htmlCode = $.htmlCodeLTStepEditor("abc", 25, 5, 5, 600);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	assert.equal(e.data("editable").value, expected["view"], "Value View Test.");
	e.click();
	var p = e.data("editableContainer").tip();
	assert.ok(p.is(":visible"), "popover was visible");
	assert.equal(p.find("input[name=finish_rps]").val(),
				 finish.toString(), "Finish RPS Test.");
	assert.equal(p.find("input[name=step_len]").val(),
				 step.toString(), "Step Length Test.");
	assert.equal(p.find("input[name=duration]").val(),
				 duration.toString(), "Duration Test.");
	assert.equal(p.find(".popover-title").text(),
				 expected["title"], "Window Title Test.");
	p.find(".editable-cancel").click();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		done();
	}, 300);
});


QUnit.test("LT Step Editor New Value Test", function(assert) {
	var done = assert.async();
	var start = 25;
	var finish = 5;
	var newFinish = 10;
	var step = 5;
	var newStep = 4;
	var duration = 600; // seconds
	var newDuration = 1000; // seconds
	var expectedView = "stepped from 25 to 10 rps, with 4 rps steps, step duration 00:16:40"; 
	var htmlCode = $.htmlCodeLTStepEditor("abc", 25, 5, 5, 600);
	var e = $(htmlCode).appendTo("#qunit-fixture").editable();
	e.click();
	var p = e.data("editableContainer").tip();
	p.find("input[name=finish_rps]").val(newFinish);
	p.find("input[name=step_len]").val(newStep);
	p.find("input[name=duration]").val(newDuration);
	p.find("form").submit();
	setTimeout(function() {
		assert.ok(!p.is(":visible"), "popover was removed");
		assert.equal(e.data("editable").value, expectedView, "New Values saved.");
		done();
	}, 300);
});
