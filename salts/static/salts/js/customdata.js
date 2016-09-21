/**
Custom data for scenario editable input.
Internally value stored as {testname: "Нагрузочный тест", duration: 180}

@class customdata
@extends customdatainput
@final
@example
<a href="#" id="customdata" data-type="customdata" data-pk="1">Нагрузочный тест</a>
<script>
$(function(){
    $('#customdata').editable({
        url: '/post',
        title: 'Изменяемые параметры',
        value: {
            testname: "Нагрузочный тест", 
            duration: 180 
        }
    });
});
</script>
**/

function bin2jsonstr(binStr) {
  return unescape(atob(binStr));
}

function jsonstr2bin(jsonStr) {
  return btoa(escape(jsonStr));
}

function getObjectsOfType(obj, key, typeName) {
  var objects = [];
  for (var i in obj) {
    if (!obj.hasOwnProperty(i)) continue;
    if (typeof obj[i] == typeName && i == key) {
        objects.push(obj[i]);
    }
    if (typeof obj[i] == 'object')
      objects = objects.concat(getObjectsOfType(obj[i], key, typeName));
  }
  return objects;
}

(function ($) {
    "use strict";
    
    var CustomData = function (options) {
        var htmlCode = "";
        var value = getObjectsOfType(options, 'value', 'string')[0];
        $.each(JSON.parse(bin2jsonstr(value)), function(section, params) {
          htmlCode += "<div name='configsection'><h2>" + section + "</h2>";
          $.each(params, function(key, value) {
            htmlCode += "<div name='configparameter'>" +
                        "<label><span>" + key + "</span>" +
                        "<input type='text' name='" + key + "' value='" +
                        value + "'>" +
                        "</label></div>";
          });
          htmlCode += "</div>";
        });
        CustomData.defaults.tpl = htmlCode;
        this.init('customdata', options, CustomData.defaults);
    };

    //inherit from Abstract input
    $.fn.editableutils.inherit(CustomData, $.fn.editabletypes.abstractinput);

    $.extend(CustomData.prototype, {
        /**
        Renders input from tpl

        @method render() 
        **/        
        render: function() {
          this.$inputs = this.$tpl.find('input');
        },
        
        /**
        Default method to show value in element. Can be overwritten by display option.
        
        @method value2html(value, element) 
        **/
        value2html: function(value, element) {
        },
        
        /**
        Gets value from element's html
            console.log("Editable: value2html: value: " + value +
                        ", element: " + JSON.stringify(element));
        
        @method html2value(html) 
        **/        
        html2value: function(html) {        
          return null;  
        },
      
       /**
        Converts value to string. 
        It is used in internal comparing (not for sending to server).
        
        @method value2str(value)  
       **/
       value2str: function(value) {
           return value;
       }, 
       
       /*
        Converts string to value. Used for reading value from 'data-value' attribute.
        
        @method str2value(str)  
       */
       str2value: function(str) {
           /*
           this is mainly for parsing value defined in data-value attribute. 
           If you will always set value by javascript, no need to overwrite it
           */
           return str;
       },                
       
       /**
        Sets value of input.
        
        @method value2input(value) 
        @param {mixed} value
       **/         
       value2input: function(value) {
          if(!value) {
            return;
          }
          var jsonObj = JSON.parse(bin2jsonstr(value));
          this.$inputs.each(function() {
            var parentSec = $(this).parents("div[name='configsection']");
            var section = parentSec.find('h2').text();
            if (jsonObj.hasOwnProperty(section)) {
              $(this).val(jsonObj[section][$(this).attr('name')]);
            }
          });
       },       
       
       /**
        Returns value of input.
        
        @method input2value() 
       **/          
       input2value: function() { 
          var jsonObj = {};
          this.$inputs.each(function() {
            var parentSec = $(this).parents("div[name='configsection']");
            var section = parentSec.find('h2').text();
            if (!jsonObj.hasOwnProperty(section)) {
              jsonObj[section] = {};
            }
            jsonObj[section][$(this).attr('name')] = $(this).val();
          });
          return jsonstr2bin(JSON.stringify(jsonObj));
       },        
       
        /**
        Activates input: sets focus on the first field.
        
        @method activate() 
       **/        
       activate: function() {
           this.$inputs.filter('[name="test_name"]').focus();
       }   
    });

    CustomData.defaults = $.extend({},
        $.fn.editabletypes.abstractinput.defaults, {
          tpl: "", 
          inputclass: ""
    });

    $.fn.editabletypes.customdata = CustomData;

}(window.jQuery));
