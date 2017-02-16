(function ($) {
	"use strict";

	var newLoad = function(option, rps, params) {
		var $tbl = $("div#load table");
		var nextId = 0;
		var $rows = $tbl.find("tr");
		$.each($rows, function() {
			var thisId = parseInt($(this).attr("id"), 10);
			if (nextId <= thisId)
				nextId = thisId + 1;
		});
		var labelCode = "<label><span>Load #{number}: </span></label>";
		var aCode = $.htmlCodeLTSelectSchedule(option, rps, params);
		var butCode = "<button type=button class='btn btn-plus' disabled>" +
						"<span class='glyphicon glyphicon-plus'></span>" +
					  "</button>";
		$tbl.append("<tr class=salts-load-row id=" + nextId + ">" +
					"<td>" + labelCode.replace("{number}", $rows.length + 1) + "</td><td>" +
					aCode + "</td><td>" + butCode + "</td></tr>");
		return $tbl.find("tr:last");
	}

	var LTConfigEditor = function (options) {
		var value = valueFromObject(options.scope, "value");
		var data = JSON.parse(bin2jsonstr(value));
		this.rps = data.rps;
		this.init("ltconfigeditor", options, LTConfigEditor.defaults);
		this.loads = [];
		this.rps_values = [];
	};

	$.fn.editableutils.inherit(LTConfigEditor, $.fn.editabletypes.abstractinput);

	$.extend(LTConfigEditor.prototype, {

		addLoad: function(option, rps, params) {
			var $row = newLoad(option, rps, params);
			var $a = $row.find("a");
			this.loads.push($a);
			$a.editable({
				showbuttons: "bottom",
				display: function(value) {
					var step = JSON.parse(bin2jsonstr(value));
					if (value == $a.attr("data-value") && $a.text())
						return;
					var desc = "";
					if (step.loadtype == "line")
						desc = "linear load from " + step.params.a + " to " +
							   step.params.b + " rps";
					else if (step.loadtype == "const")
						desc = "constant load for " + step.params.a + " rps";
					else if (step.loadtype == "step")
						desc = "stepped load from " + step.params.a + " to " +
							   step.params.b + " rps";
					$a.attr("data-value", value);
					$a.text(desc);
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
			$("div#load table").find("tr").remove();
			var changed = JSON.parse(bin2jsonstr(value));
			this.loads = [];
			this.rps_values = [];
			this.$input.filter("[name=test_name]").val(changed["test_name"]);
			var rps = 1;
			for (var i = 0; i < changed.steps.length; i++) {
				var lt = changed.steps[i].loadtype;
				var params = changed.steps[i].params;
				this.addLoad(lt, rps, params);
				rps = (lt == "const" ? params.a : params.b);
				this.rps_values.push(rps);
			}
			this.$input.filter("[name=target]").val(changed["target"]);
			this.$input.filter("[name=port]").val(changed["port"]);
			this.target_port = changed["s"];
		},
       
		input2value: function() {
			var steps = [];
			$.each(this.loads, function() {
				var step = JSON.parse(bin2jsonstr($(this).attr("data-value")));
				steps.push(step);
			});
			var changed = {
				test_name: this.$input.filter("[name='test_name']").val(),
				steps: steps,
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
				 "<div id=load>" +
					"<table>" +
					"</table>" +
				 "</div>" +
				 "<div><label><span>Target: </span></label>" +
					"<input type='text' name='target'></input>" +
				 	"<label><span>Port: </span></label>" +
					"<input type='text' name='port'></input></div>",
			inputclass: ""
	});

	$.fn.editabletypes.ltconfigeditor = LTConfigEditor;

}(window.jQuery));
