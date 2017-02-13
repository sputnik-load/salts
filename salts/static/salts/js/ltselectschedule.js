(function ($) {
	"use strict";

	$.LTSelectOptions = {no: "Select To Add New Scheme",
						 const: "Constant Load For {rps} RPS",
						 step: "Stepped Load From {rps} RPS"};

	$.htmlCodeLTSelectSchedule = function(option, rps) {
		var srcData = [];
		for (var k in $.LTSelectOptions) {
			if (k == "no" && option != k)
				continue;
			srcData.push([k,
						  $.LTSelectOptions[k].replace("{rps}", rps)]);
		}
		var selectedValue = $.LTSelectOptions[option].replace("{rps}", rps);
		var srcValuesLine = JSON.stringify(srcData);
		return "<a href=# data-type=ltselectschedule " +
				"data-rps=" + rps + " " +
				"data-value='" + selectedValue + "' " +
				"data-source='" + srcValuesLine + "'></a>";
	}


	var loadScheduleParam = function(th, $ss) {
		$ss.find("#param").detach();
		var value = $ss.find("#schedule").val();
		if (value == "const")
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
		this.$constParam = $("<div id=param>" +
							 "<label><span>Duration: </span></label>" +
							 	"<input type=text name=duration></input>" +
							 "</div>");
		this.$stepParam = $("<div id=param>" +
							"<label><span>Finish RPS: </span></label>" +
								"<input type=text name=finish-rps></input><br>" +
							"<label><span>Step Length: </span></label>" +
								"<input type=text name=step-len></input><br>" +
							"<label><span>Duration: </span></label>" +
								"<input type=text name=duration></input>" +
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
			$schedule.on("change", function() {
				loadScheduleParam(th, $("#select-schedule"));
			});
			for (var i = 0; i < this.source.length; i++) {
				var item = this.source[i];
				if (item[0] == "no" && item[1] != value)
					continue;
				$("#schedule").append($("<option></option>")
										.attr("value", item[0])
										.text(item[1]));
				if (item[1] == value) {
					$schedule.val(item[0]);
					loadScheduleParam(th, $("#select-schedule"));
				}
			}
		},
       
		input2value: function() {
			return $("#schedule option:selected").text();
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
