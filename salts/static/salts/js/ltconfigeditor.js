(function ($) {
	"use strict";

	var assignLoadLabels = function() {
		var $tbl = $("div#load table");
		var labelCode = "<label><span>Load #{number}: </span></label>";
		var i = 1;
		$.each($tbl.find("tr"), function() {
			$(this).find("td:first").html(labelCode.replace("{number}", i));
			i += 1;
		});
	}

	var newLoad = function(option, id, rps, params) {
		var $tbl = $("div#load table");
		var $rows = $tbl.find("tr");
		var $row = $tbl.find("tr#" + id);
		var newId = 0;
		if (!$row.length)
			newId = id;
		else {
			$.each($rows, function() {
				var thisId = parseInt($(this).attr("id"), 10);
				if (newId <= thisId)
					newId = thisId + 1;
			});
		}
		var aCode = $.htmlCodeLTSelectSchedule(option, rps, params);
		var plusCode = "<button type=button name=add class='btn btn-plus'>" +
					   "<span class='glyphicon glyphicon-plus'></span>" +
					   "</button>";
		var delCode = "<button type=button name=del class='btn btn-sm'>" +
					  "<span class='glyphicon glyphicon-remove'></span>" +
					  "</button>";
		var rowCode = "<tr class=salts-load-row id=" + newId + "><td></td>" +
					  "<td>" + aCode + "</td><td>" + plusCode + "</td>" +
					  "<td>" + delCode + "</td></tr>"
		if ($row.length)
			$(rowCode).insertAfter($row);
		else
			$tbl.append(rowCode);
		assignLoadLabels();

		return $tbl.find("tr#" + newId);
	}

	var LTConfigEditor = function (options) {
		var value = valueFromObject(options.scope, "value");
		var data = JSON.parse(bin2jsonstr(value));
		this.rps = data.rps;
		this.init("ltconfigeditor", options, LTConfigEditor.defaults);
	};

	$.fn.editableutils.inherit(LTConfigEditor, $.fn.editabletypes.abstractinput);

	$.extend(LTConfigEditor.prototype, {

		addLoad: function(option, id, rps, params) {
			if (!params)
				params = {};
			var $row = newLoad(option, id, rps, params);
			var $a = $row.find("a");
			$a.editable({
				showbuttons: "bottom",
				display: function(value) {
					var step = JSON.parse(bin2jsonstr(value));
					if (value == $a.attr("data-value") && $a.text())
						return;
					var desc = "select to add new scheme";
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
			$row.find("button[name=add]").on("click", function() {
				var new_rps = rps;
				if (params) {
					new_rps = params.b;
					if (option == "const")
						new_rps = params.a;
				}
				configEditor.addLoad("no", $row.attr("id"), rps);
			});
			$row.find("button[name=del]").on("click", function() {
				$row.remove();
				assignLoadLabels();
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
			this.$input.filter("[name=test_name]").val(changed["test_name"]);
			var rps = 1;
			for (var i = 0; i < changed.steps.length; i++) {
				var loadtype = changed.steps[i].loadtype;
				var params = changed.steps[i].params;
				this.addLoad(loadtype, i, rps, params);
				rps = (loadtype == "const" ? params.a : params.b);
			}
			this.$input.filter("[name=target]").val(changed["target"]);
			this.$input.filter("[name=port]").val(changed["port"]);
			this.target_port = changed["s"];
		},
       
		input2value: function() {
			var steps = [];
			var $tbl = $("div#load table");
			$.each($tbl.find("tr a"), function() {
				var step = JSON.parse(bin2jsonstr($(this).attr("data-value")));
				steps.push(step);
			});
			var changed = {
				test_name: this.$input.filter("[name=test_name]").val(),
				steps: steps,
				target: this.$input.filter("[name=target]").val(),
				port: this.$input.filter("[name=port]").val(),
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
