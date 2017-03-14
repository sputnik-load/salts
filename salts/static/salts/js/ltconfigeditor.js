(function ($) {
	"use strict";

	var assignLoadLabels = function(gen) {
		var $tbl = $("div#load");
		var titleTemplate = Lang.tr.run_page.test_name.config_editor.label +
							" #{number}";
		// var labelCode = "<label class='circleBase rps-schedule-nn'><span>{title}</span></label>";
		var labelCode = "<label class=badge><span>{title}</span></label>";
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
		var butCode = "<button type=button name=add class='btn btn-sm add-load'>" +
					   "<span class='glyphicon glyphicon-plus'></span>" +
					   "</button>";
		butCode += "<span style='padding-left: 10px;'></span>";
		butCode += "<button type=button name=del class='btn btn-sm del-load'>" +
				   "<span class='glyphicon glyphicon-remove'></span>" +
				   "</button>";
		var rowCode = "<div class=row id=" + newId + ">";
		rowCode += "<div name=nn class='col-sm-2 salts-load-row' align=right></div>";
		rowCode += "<div name=editable class='col-sm-6' align=left>" + aCode + "</div>";
		rowCode += "<div name=buttons class='col-sm-4' align=left>" + butCode + "</div>";
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
				placement: "right",
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
			this.$tpl.find("label[name=hostname] span").text(tr_config_editor.target.hostname + ":");
			this.$tpl.find("label[name=port] span").text(tr_config_editor.target.port + ":");
			$("legend[name=schedule-editor]").text(tr_config_editor.load_param_title);
			$("legend[name=target]").text(tr_config_editor.target_title);
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
			$("div#load div.row").remove();
			var changed = JSON.parse(bin2jsonstr(value));
			this.$input.filter("[name=test_name]").val(changed["test_name"]);
			var rps = 1;
			for (var i = 0; i < changed.steps.length; i++) {
				var loadtype = changed.steps[i].loadtype;
				var params = changed.steps[i].params;
				this.addLoad(loadtype, i, rps, params);
				rps = (loadtype == "const" ? params.a : params.b);
			}
			this.$input.filter("[name=hostname]").val(changed["hostname"]);
			this.$input.filter("[name=port]").val(changed["port"]);
			this.target_port = changed["s"];
		},
       
		input2value: function() {
			var steps = [];
			var $tbl = $("div#load");
			$.each($tbl.find("div.row a"), function() {
				var step = JSON.parse(bin2jsonstr($(this).attr("data-value")));
				steps.push(step);
			});
			var changed = {
				test_name: this.$input.filter("[name=test_name]").val(),
				steps: steps,
				hostname: this.$input.filter("[name=hostname]").val(),
				port: this.$input.filter("[name=port]").val(),
				s: this.target_port
			};
			return jsonstr2bin(JSON.stringify(changed));
		},
       
		activate: function() {
			this.$input.filter("[name=test_name]").focus();
		}
	});

	LTConfigEditor.defaults = $.extend({},
		$.fn.editabletypes.abstractinput.defaults, {
			tpl: "<div name=test-name class=row>" +
					"<label name=test-name class=col-sm-4><span align=right></span></label>" +
					"<input type=text name=test_name class=col-sm-7 align=left></input></div>" +
				 "</div>" +
				 "<div name=rps-schedule>" +
					"<fieldset class=salts-load-editor>" +
					"<legend name=schedule-editor class=salts-load-editor></legend>" +
					"<div id=load>" +
					"</div>" +
				 "</fieldset></div>" +
				 "<div name=target>" +
					"<fieldset class=salts-load-editor>" +
					"<legend name=target class=salts-load-editor></legend>" +
						"<div name=hostname class='row'>" +
							"<label name=hostname class=col-sm-4><span></span></label>" +
							"<input type=text name=hostname class=col-sm-7></input>" +
						"</div>" +
						"<div name=port class='row top-buffer'>" +
							"<label name=port class=col-sm-4><span></span></label>" +
							"<input type=text name=port class=col-sm-7></input>" +
						"</div>" +
					"</fieldset></div>",
			inputclass: ""
	});

	$.fn.editabletypes.ltconfigeditor = LTConfigEditor;

}(window.jQuery));
