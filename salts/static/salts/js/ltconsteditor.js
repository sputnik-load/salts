(function ($) {
	"use strict";

	var timeRegex = "(\\d\\d:\\d\\d:\\d\\d)";
	var valueTemplate = "constant for {rps} rps for {duration}";
	var titleTemplate = "Constant Load For {rps} rps";

	var LTConstEditor = function (options) {
		this.init("ltconsteditor", options, LTConstEditor.defaults);
	};

	$.fn.editableutils.inherit(LTConstEditor, $.fn.editabletypes.abstractinput);

	$.extend(LTConstEditor.prototype, {

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
			if (!value)
				return;
			var templ = valueTemplate.replace("{rps}", "(\\d+)");
			templ = templ.replace("{duration}", timeRegex);
			var result = value.match(templ);
			if (result == null)
				return;
			this.rps = parseInt(result[1], 10);
			this.$input.filter("[name='testlen']").val(fromHHMMSS(result[2]));
		},
       
		input2value: function() {
			var value = valueTemplate.replace("{rps}", this.rps);
			value = value.replace("{duration}",
								  toHHMMSS(this.$input.filter("[name='testlen']").val()));
			return value;
		},
       
		activate: function() {
			this.$input.filter("[name='test_name']").focus();
		}
	});

	LTConstEditor.defaults = $.extend({},
		$.fn.editabletypes.abstractinput.defaults, {
			tpl: "<div><label><span>Const Len: </span></label><input type='text' name='testlen'></label></div>",
			inputclass: ""
	});

	$.fn.editabletypes.ltconsteditor = LTConstEditor;

	$.htmlCodeLTConstEditor = function(id, rps, seconds) {
		var value = valueTemplate.replace("{rps}", rps);
		value = value.replace("{duration}", toHHMMSS(seconds));
		var title = titleTemplate.replace("{rps}", rps);;
		return "<a href='#' id='" + id + "' data-type='ltconsteditor' " +
			   "data-value='" + value + "' " +
			   "data-title='" + title + "' " +
			   "></a>";
	}

}(window.jQuery));

