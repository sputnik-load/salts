(function ($) {
	"use strict";

	$.LTSelectOptions = {no: Lang.tr.run_page.test_name.select_schedule.options.no,
						 line: Lang.tr.run_page.test_name.select_schedule.options.line,
						 const: Lang.tr.run_page.test_name.select_schedule.options.const,
						 step: Lang.tr.run_page.test_name.select_schedule.options.step};

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

	$.htmlCodeLTSelectSchedule = function(option, rps, gen, params) {
		var srcData = [];
		var selectedValue = "";
		if (!params)
			params = {};
		for (var k in $.LTSelectOptions) {
			if ((k == "no") && (!$.isEmptyObject(params)))
				continue;
			srcData.push({value: k, text: $.LTSelectOptions[k]});
			if (k == option) {
				var s = JSON.stringify({loadtype: option,
										params: params})
				selectedValue = jsonstr2bin(s);
			}
		}
		return "<a href=# data-type=ltselectschedule " +
				"data-rps=" + rps + " " +
				"data-gen=" + gen + " " +
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
		$("legend[name=schedule-step-editor]").text(Lang.tr.run_page.test_name.config_editor.load.param_title);
	}

	var LTSelectSchedule = function (options) {
		var appendRow = function(par_name, par_value, value) {
			if (typeof value === "undefined")
				value = ""
			return "<div class='row top-buffer'>" +
					"<label class='col-sm-4'><span>" + par_value + ":</span></label>" +
					"<input class='col-sm-7' type=text name='" + par_name + "'>" +
						value + "</input>" +
				   "</div>";
		};
		this.init("ltselectschedule", options, LTSelectSchedule.defaults);
		this.rps = valueFromObject(this.options.scope, "rps");
		this.gen = valueFromObject(this.options.scope, "gen");
		this.source = valueFromObject(this.options.scope, "source");
		var tr_load = Lang.tr.run_page.test_name.config_editor.load;
		var divWithTitle = "<div id=param><fieldset class=salts-load-editor>" +
						   "<legend name=schedule-step-editor class=salts-load-editor></legend>" +
						   "{paramlist}</fieldset></div>";
		var htmlCode = appendRow("a", tr_load.line.a) +
					   appendRow("b", tr_load.line.b) +
					   appendRow("dur", tr_load.line.dur);
		this.$lineParam = $(divWithTitle.replace("{paramlist}", htmlCode));
		htmlCode = appendRow("a", tr_load.const.a) +
				   appendRow("dur", tr_load.const.dur);
		this.$constParam = $(divWithTitle.replace("{paramlist}", htmlCode));
		var htmlCode = appendRow("a", tr_load.step.a) +
					   appendRow("b", tr_load.step.b) +
					   appendRow("step", tr_load.step.step) +
					   appendRow("dur", tr_load.step.dur);
		this.$stepParam = $(divWithTitle.replace("{paramlist}", htmlCode));
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
			$schedule.attr("disabled", this.gen == "jmeter");
			if ($.isEmptyObject(step.params))
				return;
			if ("dur" in step.params)
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
				if (k != "step" && k != "dur")
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
			tpl: "<div id=select-schedule style='width: 400px;'><select id=schedule>" +
				 	  "</select>" +
					  "<div id=param></div>" +
				 "</div>",
			inputclass: ""
	});

	$.fn.editabletypes.ltselectschedule = LTSelectSchedule;
}(window.jQuery));
