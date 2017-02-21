(function ($) {
	"use strict";

	$.LTSelectOptions = {no: "Select To Add New Scheme",
						 line: "Linear Load From {rps} RPS",
						 const: "Constant Load For {rps} RPS",
						 step: "Stepped Load From {rps} RPS"};

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
				th.$input = th.$tpl.find("div#param input");
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
			this.$input = this.$tpl.find("div#param input");
			for (var name in step.params) {
				this.$input.filter("[name=" + name + "]").val(step.params[name]);
			}
		},
       
		input2value: function() {
			var $schedule = $("#schedule");
			var params = {};
			$.each(this.$input, function() {
				params[$(this).attr("name")] = $(this).val();
			});
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
