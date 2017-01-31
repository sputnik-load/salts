(function ($) {
	"use strict";

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
			if (!value) {
				return;
			}
			console.log("testing3195. value: " + value);
			this.$input.filter("[name='testlen']").val(ms2sec(value));
		},
       
		input2value: function() {
			var testlen = sec2ms(this.$input.filter("[name='testlen']")).val();
			return testlen;
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

}(window.jQuery));
