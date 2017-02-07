(function ($) {
	"use strict";

	$.LTSelectOptions = {no: "Select To Add New Scheme",
						 const: "Constant Load For {rps} RPS",
						 step: "Stepped Load From {rps} RPS"};

	$.htmlCodeLTSelectSchedule = function(option, rps) {
		var srcData = [];
		for (var k in $.LTSelectOptions) {
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

	var LTSelectSchedule = function (options) {
		this.init("ltselectschedule", options, LTSelectSchedule.defaults);
		this.rps = valueFromObject(this.options.scope, "rps");
		this.source = valueFromObject(this.options.scope, "source");
		this.value = valueFromObject(this.options.scope, "value");
		this.$constParam = $("<div id=param>" +
							 "<label><span>Duration: </span></label>" +
							 	"<input type=text name=duration></input>" +
							 "</div>");
		this.$stepParam = $("<div id=param>" +
							"<label><span>Finish RPS: </span></label>" +
								"<input type=text name=finish-rps></input>" +
							"<label><span>Step Length: </span></label>" +
								"<input type=text name=step-len></input>" +
							"<label><span>Duration: </span></label>" +
								"<input type=text name=duration></input>" +
							 "</div>");
	};

	$.fn.editableutils.inherit(LTSelectSchedule, $.fn.editabletypes.abstractinput);

	$.extend(LTSelectSchedule.prototype, {

		render: function() {
			console.log("LTSelectSchedule: render");
			for (var i = 0; i < this.source.length; i++) {
				var item = this.source[i];
				$("#schedule").append($("<option></option>")
										.attr("value", item[0])
										.text(item[1]));
				if (this.value == item[1])
					$("#schedule").val(item[0]);
			}
			var $constParam = this.$constParam;
			var $stepParam = this.$stepParam;
			$("#schedule").on("change", function() {
				if (this.value == "const") {
					$("#select-schedule").find("#param").detach();
					$constParam.appendTo("#select-schedule");	
				}
				else if (this.value == "step") {
					$("#select-schedule").find("#param").detach();
					$stepParam.appendTo("#select-schedule");	
				}
				else {
					$("#select-schedule").find("#param").detach();
					$("<div id=param></div>").appendTo("#select-schedule");
				}
			});
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
			// console.log("value2input: value: " + value);
			// console.log("value2input: this.rps: " + this.rps);
			// console.log("value2input: this.source: " + this.source);
			if (!value)
				return;	
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
