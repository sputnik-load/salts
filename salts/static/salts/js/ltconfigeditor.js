/**
Custom data for scenario editable input.
**/

function bin2jsonstr(binStr) {
  return decodeURIComponent(atob(binStr));
}

function jsonstr2bin(jsonStr) {
  return btoa(encodeURIComponent(jsonStr));
}

(function ($) {
	"use strict";

	var LTConfigEditor = function (options) {
		this.init("ltconfigeditor", options, LTConfigEditor.defaults);
	};

	$.fn.editableutils.inherit(LTConfigEditor, $.fn.editabletypes.abstractinput);

	$.extend(LTConfigEditor.prototype, {

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
			var changed = JSON.parse(bin2jsonstr(value));
			var ms2sec = function(ms) { return ms / 1000; }
			this.$input.filter("[name='test_name']").val(changed["test_name"]);
			this.$input.filter("[name='rps']").val(changed["rps"]);
			this.$input.filter("[name='rampup']").val(ms2sec(changed["rampup"]));
			this.$input.filter("[name='testlen']").val(ms2sec(changed["testlen"]));
			this.$input.filter("[name='rampdown']").val(ms2sec(changed["rampdown"]));
			this.$input.filter("[name='target']").val(changed["target"]);
			this.$input.filter("[name='port']").val(changed["port"]);
			this.target_port = changed["s"];
		},
       
		input2value: function() {
			var sec2ms = function(sec) { return sec * 1000; }
			var changed = {
				test_name: this.$input.filter("[name='test_name']").val(),
				rps: this.$input.filter("[name='rps']").val(),
				rampup: sec2ms(this.$input.filter("[name='rampup']").val()),
				testlen: sec2ms(this.$input.filter("[name='testlen']").val()),
				rampdown: sec2ms(this.$input.filter("[name='rampdown']").val()),
				target: this.$input.filter("[name='target']").val(),
				port: this.$input.filter("[name='port']").val(),
				s: this.target_port
			};
			return jsonstr2bin(JSON.stringify(changed));
		},
       
		activate: function() {
			this.$input.filter('[name="test_name"]').focus();
		}
	});

	LTConfigEditor.defaults = $.extend({},
		$.fn.editabletypes.abstractinput.defaults, {
			tpl: "<div><label><span>Имя теста: </span></label><input type='text' name='test_name'></label></div>" +
				 "<div><label><span>RPS: </span></label><input type='text' name='rps'></label></div>" +
				 "<div><label><span>Ramp Up: </span></label><input type='text' name='rampup'></label></div>" +
				 "<div><label><span>Const Len: </span></label><input type='text' name='testlen'></label></div>" +
				 "<div><label><span>Ramp Down: </span></label><input type='text' name='rampdown'></label></div>" +
				 "<div><label><span>Target: </span></label><input type='text' name='target'></label>" +
				 "<label><span>Port: </span></label><input type='text' name='port'></label></div>",
			inputclass: ""
	});

	$.fn.editabletypes.ltconfigeditor = LTConfigEditor;

}(window.jQuery));
