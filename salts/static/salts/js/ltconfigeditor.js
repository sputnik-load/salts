(function ($) {
	"use strict";

	var addLoad = function(option, rps) {
		var $tbl = $("div#load table");
		var labelCode = "<label><span>Load: </span></label>";
		var aCode = $.htmlCodeLTSelectSchedule(option, rps);
		var butCode = "<button type=button class='btn btn-plus' disabled>" +
						"<span class='glyphicon glyphicon-plus'></span>" +
					  "</button>";
		$tbl.append("<tr class=salts-load-row><td>" + labelCode + "</td><td>" +
					aCode + "</td><td>" + butCode + "</td></tr>");
		return $tbl.find("tr:last");
	}

	var LTConfigEditor = function (options) {
		console.log("Init LTConfigEditor. Options: " + JSON.stringify(options));
		var value = valueFromObject(options.scope, "value");
		var data = JSON.parse(bin2jsonstr(value));
		this.rps = data.rps;
		console.log("Init LTConfigEditor. RPS: " + this.rps);
		this.init("ltconfigeditor", options, LTConfigEditor.defaults);
	};

	$.fn.editableutils.inherit(LTConfigEditor, $.fn.editabletypes.abstractinput);

	$.extend(LTConfigEditor.prototype, {

		render: function() {
			this.$input = this.$tpl.find("input");
			var $row = addLoad("no", this.rps);
			this.$load = $row.find("a");
			var $load = this.$load;
			this.$load.editable({
				display: function(value) {
					console.log("Load. value: " + value);
					$load.text(value);
				}
			});
			this.$load.on("save", function(e, params) {
				var disabled = (params.newValue == $.LTSelectOptions.no);
				$row.find("button").attr("disabled", disabled);
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
			if (!value) {
				return;
			}
			var changed = JSON.parse(bin2jsonstr(value));
			this.$input.filter("[name='test_name']").val(changed["test_name"]);
			this.$input.filter("[name='rps']").val(changed["rps"]);
			this.$input.filter("[name='rampup']").val(ms2sec(changed["rampup"]));
			/*this.$input.filter("[name='testlen']").val(ms2sec(changed["testlen"]));*/
			this.$input.filter("[name='rampdown']").val(ms2sec(changed["rampdown"]));
			this.$input.filter("[name='target']").val(changed["target"]);
			this.$input.filter("[name='port']").val(changed["port"]);
			this.target_port = changed["s"];
		},
       
		input2value: function() {
			var changed = {
				test_name: this.$input.filter("[name='test_name']").val(),
				rps: this.$input.filter("[name='rps']").val(),
				rampup: sec2ms(this.$input.filter("[name='rampup']").val()),
				/*testlen: sec2ms(this.$input.filter("[name='testlen']").val()),*/
				rampdown: sec2ms(this.$input.filter("[name='rampdown']").val()),
				target: this.$input.filter("[name='target']").val(),
				port: this.$input.filter("[name='port']").val(),
				s: this.target_port
			};
			return jsonstr2bin(JSON.stringify(changed));
		},
       
		activate: function() {
			this.$input.filter("[name='test_name']").focus();
		}
	});

	LTConfigEditor.defaults = $.extend({},
		$.fn.editabletypes.abstractinput.defaults, {
			tpl: "<div><label><span>Имя теста: </span></label>" +
					"<input type='text' name='test_name'></input></div>" +
				 "<div><label><span>RPS: </span></label>" +
					"<input type='text' name='rps'></input></div>" +
				 "<div><label><span>Ramp Up: </span></label>" +
			     "<input type='text' name='rampup'></input></div>" +
				 "<div id=load>" +
					"<table>" +
					"</table>" +
				 "</div>" +
				 "<div><label><span>Ramp Down: </span></label>" +
					"<input type='text' name='rampdown'></input></div>" +
				 "<div><label><span>Target: </span></label>" +
					"<input type='text' name='target'></input>" +
				 	"<label><span>Port: </span></label>" +
					"<input type='text' name='port'></input></div>",
			inputclass: ""
	});

	$.fn.editabletypes.ltconfigeditor = LTConfigEditor;

}(window.jQuery));
