QUnit.test("toHHMMSS", function(assert) {
	assert.equal(toHHMMSS(10000), "02:46:40", "The usual case.");
	assert.equal(toHHMMSS(0), "00:00:00", "Zero case.");
	assert.equal(toHHMMSS("a"), "Incorrect input", "Negative case.");
});


QUnit.test("fromHHMMSS", function(assert) {
	assert.equal(fromHHMMSS("02:46:40"), "10000", "The usual case.");
	assert.equal(fromHHMMSS("00:00:00"), "0", "Zero case.");
	assert.equal(fromHHMMSS("00:00"), "Incorrect input", "Negative case #1.");
	assert.equal(fromHHMMSS("231:00"), "Incorrect input", "Negative case #2.");
	assert.equal(fromHHMMSS("abc"), "Incorrect input", "Negative case #3.");
});
