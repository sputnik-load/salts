(function ($) {
	"use strict";


	var valueTemplate = "stepped from {start} to {finish} rps, " +
						"with {step} rps steps, step duration {duration}";
	var titleTemplate = "Stepped Load From {start} RPS";

	var LTStepEditor = function (options) {
		this.init("ltstepeditor", options, LTStepEditor.defaults);
	};

	$.fn.editableutils.inherit(LTStepEditor, $.fn.editabletypes.abstractinput);

	$.extend(LTStepEditor.prototype, {

		render: function() {
			this.$input = this.$tpl.find("input");
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
			if (!value) {
				return;
			}
			var numRegex = "(\\d+)";
			var timeRegex = "(\\d\\d:\\d\\d:\\d\\d)";
			var templ = valueTemplate.replace("{start}", numRegex);
			templ = templ.replace("{finish}", numRegex);
			templ = templ.replace("{step}", numRegex);
			templ = templ.replace("{duration}", timeRegex);
			var result = value.match(templ);
			if (!result)
				return;
			this.start_rps = parseInt(result[1], 10);
			this.$input.filter("[name=finish_rps]").val(result[2]);
			this.$input.filter("[name=step_len]").val(result[3]);
			this.$input.filter("[name=duration]").val(fromHHMMSS(result[4]));
		},
       
		input2value: function() {
			var value = valueTemplate.replace("{start}", this.start_rps);
			value = value.replace("{finish}", this.$input.filter("[name=finish_rps]").val());
			value = value.replace("{step}", this.$input.filter("[name=step_len]").val());
			value = value.replace("{duration}",
								  toHHMMSS(this.$input.filter("[name=duration]").val()));
			return value;
		},
       
		activate: function() {
		}
	});

	LTStepEditor.defaults = $.extend({},
		$.fn.editabletypes.abstractinput.defaults, {
			tpl: "<div>" +
					"<label><span>Finish RPS: </span></label>" +
						"<input type='text' name='finish_rps'></input>" +
					"<label><span>Step Length: </span></label>" +
						"<input type='text' name='step_len'></input>" +
					"<label><span>Duration: </span></label>" +
						"<input type='text' name='duration'></input>" +
				 "</div>",
			inputclass: ""
	});

	$.fn.editabletypes.ltstepeditor = LTStepEditor;

	$.htmlCodeLTStepEditor = function(id, start, finish, step, duration) {
		var title = titleTemplate.replace("{start}", start);
		var value = valueTemplate.replace("{start}", start);
		value = value.replace("{finish}", finish);
		value = value.replace("{step}", step);
		value = value.replace("{duration}", toHHMMSS(duration));
		return "<a href='#' id='" + id + "' data-type='ltstepeditor' " +
			   "data-value='" + value + "' " +
			   "data-title='" + title + "' " +
			   "></a>";
	}
}(window.jQuery));
