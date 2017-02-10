(function ($) {
	"use strict";

	var newLoad = function(option, rps) {
		var $tbl = $("div#load table");
		var nextId = 0;
		$.each($tbl.find("tr"), function() {
			var thisId = parseInt($(this).attr("id"), 10);
			if (nextId <= thisId)
				nextId = thisId + 1;
		});
		var labelCode = "<label><span>Load: </span></label>";
		var aCode = $.htmlCodeLTSelectSchedule(option, rps);
		var butCode = "<button type=button class='btn btn-plus' disabled>" +
						"<span class='glyphicon glyphicon-plus'></span>" +
					  "</button>";
		$tbl.append("<tr class=salts-load-row id=" + nextId + ">" +
					"<td>" + labelCode + "</td><td>" +
					aCode + "</td><td>" + butCode + "</td></tr>");
		return $tbl.find("tr:last");
	}

	var LTConfigEditor = function (options) {
		var value = valueFromObject(options.scope, "value");
		var data = JSON.parse(bin2jsonstr(value));
		this.rps = data.rps;
		this.init("ltconfigeditor", options, LTConfigEditor.defaults);
		this.loads = [];
	};

	$.fn.editableutils.inherit(LTConfigEditor, $.fn.editabletypes.abstractinput);

	$.extend(LTConfigEditor.prototype, {

		addLoad: function(option) {
			var $row = newLoad(option, this.rps);
			var $a = $row.find("a");
			this.loads.push($a);
			$a.editable({
				showbuttons: "bottom",
				display: function(value) {
					$a.text(value);
				}
			});
			$a.on("save", function(e, params) {
				var disabled = (params.newValue == $.LTSelectOptions.no);
				$row.find("button").attr("disabled", disabled);
			});
			var configEditor = this;
			var $but = $row.find("button");
			$but.on("click", function() {
				configEditor.addLoad("no");
				$but.toggleClass("btn-sm");
				$but.find("span").toggleClass("glyphicon-remove");
				$but.off("click");
				$but.on("click", function() {
					$row.remove();
				});
			});
		},

		render: function() {
			this.$input = this.$tpl.find("input");
			this.addLoad("no");
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
