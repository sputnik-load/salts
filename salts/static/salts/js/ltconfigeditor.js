(function ($) {
	"use strict";

	var assignLoadLabels = function(gen) {
		var $tbl = $("div#load");
		var titleTemplate = Lang.tr.run_page.test_name.config_editor.label +
							" #{number}";
		var labelCode = "<label class='circleBase rps-schedule-nn'><span>{title}</span></label>";
		var i = 1;
		$.each($tbl.find("div.row"), function() {
			var title = titleTemplate.replace("{number}", i);
			$(this).find("div[name=nn]").html(labelCode.replace("{title}", i));
			$(this).find("div[name=editable] a").attr("data-title", title + " (" + gen + ")");
			i += 1;
		});
	};

	var newLoad = function(option, id, rps, gen, params) {
		var $tbl = $("div#load");
		var $rows = $tbl.find("div.row");
		var $row = $rows.filter("[id=" + id + "]");
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
		var aCode = $.htmlCodeLTSelectSchedule(option, rps, gen, params);
		var plusCode = "<button type=button name=add class='btn btn-plus'>" +
					   "<span class='glyphicon glyphicon-plus'></span>" +
					   "</button>";
		var delCode = "<button type=button name=del class='btn btn-sm'>" +
					  "<span class='glyphicon glyphicon-remove'></span>" +
					  "</button>";
		var rowCode = "<div class=row id=" + newId + ">";
		rowCode += "<div name=nn class='col-sm-2 salts-load-row' align=right></div>";
		rowCode += "<div name=editable class='col-sm-6' align=left>" + aCode + "</div>";
		rowCode += "<div name=plus class='col-sm-2' align=right>" + plusCode + "</div>";
		rowCode += "<div name=del class='col-sm-2' align=left>" + delCode + "</div>";
		rowCode += "</div>";
		if ($row.length)
			$(rowCode).insertAfter($row);
		else
			$tbl.append(rowCode);
		assignLoadLabels(gen);

		return $tbl.find("div.row").filter("[id=" + newId + "]");
	};


	$.htmlCodeLTConfigEditor = function(id, title, data, text) {
		var gen = data.gen_type;
		return "<a href=# id='" + id + "'" +
			   "data-type=ltconfigeditor " +
			   "data-gen-type='" + gen + "' " +
			   "data-placement=right " +
			   "data-value='" +
			   jsonstr2bin(JSON.stringify(data)) + "'" +
			   "data-title='" + title + " (" + gen + ")'>" + text + "</a>";
	};

	var LTConfigEditor = function (options) {
		var value = valueFromObject(options.scope, "value");
		var data = JSON.parse(bin2jsonstr(value));
		this.rps = data.rps;
		this.gen = data.gen_type;
		this.init("ltconfigeditor", options, LTConfigEditor.defaults);
	};

	$.fn.editableutils.inherit(LTConfigEditor, $.fn.editabletypes.abstractinput);

	$.extend(LTConfigEditor.prototype, {

		addLoad: function(option, id, rps, params) {
			if (!params)
				params = {};
			var $row = newLoad(option, id, rps, this.gen, params);
			var $a = $row.find("a");
			$a.editable({
				showbuttons: "bottom",
				display: function(value) {
					var step = JSON.parse(bin2jsonstr(value));
					if (value == $a.attr("data-value") && $a.text())
						return;
					var tr_load = Lang.tr.run_page.test_name.config_editor.load;
					var desc = tr_load.no.desc;
					if (step.loadtype == "line") {
						desc = tr_load.line.desc.replace("{a}", step.params.a);
						desc = desc.replace("{b}", step.params.b);
					}
					else if (step.loadtype == "const")
						desc = tr_load.const.desc.replace("{a}", step.params.a);
					else if (step.loadtype == "step") {
						desc = tr_load.step.desc.replace("{a}", step.params.a);
						desc = desc.replace("{b}", step.params.b);
					}
					$a.attr("data-value", value);
					$a.text(desc);
				}
			});
			$a.on("save", function(e, params) {
				var decoded = bin2jsonstr(params.newValue);
				var disabled = (decoded.loadtype == $.LTSelectOptions.no);
				$row.find("button").attr("disabled", disabled);
			});
			var configEditor = this;
			var $buts = $row.find("button");
			$buts.attr("disabled", this.gen == "jmeter");
			$buts.filter("[name=add]").on("click", function() {
				var new_rps = rps;
				if (params) {
					new_rps = params.b;
					if (option == "const")
						new_rps = params.a;
				}
				configEditor.addLoad("no", $row.attr("id"), rps);
			});
			$buts.filter("[name=del]").on("click", function() {
				$row.remove();
				assignLoadLabels();
			});
		},

		render: function() {
			this.$input = this.$tpl.find("input");
			var tr_config_editor = Lang.tr.run_page.test_name.config_editor;
			this.$tpl.find("label[name=test-name] span").text(tr_config_editor.test_name + ":");
			this.$tpl.find("label[name=target] span").text(tr_config_editor.target + ":");
			this.$tpl.find("label[name=port] span").text(tr_config_editor.port + ":");
			$("legend[name=schedule-editor]").text(tr_config_editor.load_param_title);
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
			tpl: "<div><label name=test-name><span></span></label>" +
					"<input type='text' name='test_name'></input></div>" +
				 "<fieldset class=salts-load-editor>" +
				 "<legend name=schedule-editor class=salts-load-editor></legend>" +
				 "<div id=load>" +

					"<table>" +
					"</table>" +

				 "</div>" +
				 "</fieldset>" +
				 "<div><label name=target><span></span></label>" +
					"<input type='text' name='target'></input>" +
					"<label name=port><span></span></label>" +
					"<input type='text' name='port'></input></div>",
			inputclass: ""
	});

	$.fn.editabletypes.ltconfigeditor = LTConfigEditor;

}(window.jQuery));
