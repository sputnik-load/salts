(function ($) {
	"use strict";

	$.LTSelectOptions = {no: "Select To Add New Scheme",
						 line: "Linear Load From {rps} RPS",
						 const: "Constant Load For {rps} RPS",
						 step: "Stepped Load From {rps} RPS"};

	var ms2hhmmss = function(ms) {
		var sec = ms2sec(ms);
		if (sec < 60)
			return sec;
		if (sec >= 60 && sec < 3600)
			return Math.floor(sec / 60) + ":" +
				   pad(sec % 60);
		else {
			var hh = Math.floor(sec / 3600);
			sec = sec % 3600;
			var mm = Math.floor(sec / 60);
			return hh + ":" + pad(mm) + ":" + pad(sec % 60)
		}
	}

	var hhmmss2ms = function(line) {
		try {
			var values = line.split(":");
			if (values.length == 1)
				return sec2ms(parseInt(values[0], 10));
			else if (values.length == 2) {
				var mm = parseInt(values[0], 10);
				var ss = parseInt(values[1], 10);
				return sec2ms(60 * mm + ss);
			}
			else if (values.length == 3) {
				var hh = parseInt(values[0], 10);
				var mm = parseInt(values[1], 10);
				var ss = parseInt(values[2], 10);
				return sec2ms(3600 * hh + 60 * mm + ss);
			}
		} catch (err) {
			console.log(err);
		}
		return 0;
	}

	$.htmlCodeLTSelectSchedule = function(option, rps, params) {
		var srcData = [];
		var selectedValue = "";
		if (!params)
			params = {};
		for (var k in $.LTSelectOptions) {
			if ((k == "no") && (!$.isEmptyObject(params)))
				continue;
			var desc = $.LTSelectOptions[k].replace("{rps}", rps);
			srcData.push({value: k, text: desc});
			if (k == option) {
				var s = JSON.stringify({loadtype: option,
										params: params})
				selectedValue = jsonstr2bin(s);
			}
		}
		return "<a href=# data-type=ltselectschedule " +
				"data-rps=" + rps + " " +
				"data-value='" + selectedValue + "' " +
				"data-source='" + JSON.stringify(srcData) + "'></a>";
	}


	var loadScheduleParam = function(th, $ss) {
		$ss.find("#param").detach();
		var value = $ss.find("#schedule").val();
		if (value == "line")
			th.$lineParam.appendTo("#select-schedule");
		else if (value == "const")
			th.$constParam.appendTo("#select-schedule");
		else if (value == "step")
			th.$stepParam.appendTo("#select-schedule");
		else
			$("<div id=param></div>").appendTo("#select-schedule");
	}

	var LTSelectSchedule = function (options) {
		this.init("ltselectschedule", options, LTSelectSchedule.defaults);
		this.rps = valueFromObject(this.options.scope, "rps");
		this.source = valueFromObject(this.options.scope, "source");
		this.$lineParam = $("<div id=param>" +
								"<label><span>Start RPS: </span></label>" +
									"<input type=text name=a></input><br>" +
								"<label><span>Finish RPS: </span></label>" +
									"<input type=text name=b></input><br>" +
								"<label><span>Duration: </span></label>" +
									"<input type=text name=dur></input>" +
							"</div>");
		this.$constParam = $("<div id=param>" +
								 "<label><span>Start RPS: </span></label>" +
									"<input type=text name=a></input><br>" +
								 "<label><span>Duration: </span></label>" +
									"<input type=text name=dur></input>" +
							 "</div>");
		this.$stepParam = $("<div id=param>" +
								"<label><span>Start RPS: </span></label>" +
									"<input type=text name=a></input><br>" +
								"<label><span>Finish RPS: </span></label>" +
									"<input type=text name=b></input><br>" +
								"<label><span>Step Length: </span></label>" +
									"<input type=text name=step></input><br>" +
								"<label><span>Duration: </span></label>" +
									"<input type=text name=dur></input>" +
							 "</div>");
	};

	$.fn.editableutils.inherit(LTSelectSchedule, $.fn.editabletypes.abstractinput);

	$.extend(LTSelectSchedule.prototype, {

		render: function() {
		},

		value2html: function(value, element) {
		},

		html2value: function(html) {
			return null;
		},

		value2str: function(value) {
			return value;
		},

		str2value: function(str) {
			return str;
		},

		value2input: function(value) {
			if (!value)
				return;
			$("#schedule option").remove();
			var th = this;
			var $schedule = $("#schedule");
			$schedule.off("change");
			$schedule.on("change", function() {
				loadScheduleParam(th, $("#select-schedule"));
			});
			var step = JSON.parse(bin2jsonstr(value));
			for (var i = 0; i < this.source.length; i++) {
				var item = this.source[i];
				if (item.value == "no" && !$.isEmptyObject(step.params))
					continue;
				$("#schedule").append($("<option></option>")
										.attr("value", item.value)
										.text(item.text));
				if (item.value == step.loadtype) {
					$schedule.val(item.value);
					loadScheduleParam(th, $("#select-schedule"));
				}
			}
			if ($.isEmptyObject(step.params))
				return;
			step.params.dur = ms2hhmmss(step.params.dur);
			for (var name in step.params) {
				this.$tpl.find("div#param input")
					.filter("[name=" + name + "]")
					.val(step.params[name]);
			}
		},
       
		input2value: function() {
			var $schedule = $("#schedule");
			var params = {};
			$.each(this.$tpl.find("div#param input"), function() {
				var k = $(this).attr("name");
				params[k] = $(this).val();
				if (k != "dur")
					try {
						params[k] = parseInt(params[k], 10);
					} catch(err) {
						console.log("Warning: " + err);
						params[k] = 1;
					}
			});
			if ("dur" in params)
				params.dur = hhmmss2ms(params.dur);
			var changed = {
				loadtype: $schedule.val(),
				params: params
			};
			return jsonstr2bin(JSON.stringify(changed));
		},
       
		activate: function() {
		}
	});

	LTSelectSchedule.defaults = $.extend({},
		$.fn.editabletypes.abstractinput.defaults, {
			tpl: "<div id=select-schedule><select id=schedule>" +
				 	  "</select>" +
					  "<div id=param></div>" +
				 "</div>",
			inputclass: ""
	});

	$.fn.editabletypes.ltselectschedule = LTSelectSchedule;
}(window.jQuery));
