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

function getObjects(obj, key) {
  var objects = [];
  for (var i in obj) {
    if (!obj.hasOwnProperty(i)) continue;
    if (typeof obj[i] == 'object') {
      if (i === key) {
        objects.push(obj[i]);
      }
      objects = objects.concat(getObjects(obj[i], key));
    }
  }
  return objects;
}

(function ($) {
    "use strict";
    
    var CustomData = function (options) {
        var htmlCode = "";
        var valueObject = getObjects(options, 'value')[0];
        $.each(valueObject, function(section, params) {
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
          /*
            you may write parsing method to get value by element's html
            e.g. "Moscow, st. Lenina, bld. 15" => {city: "Moscow", street: "Lenina", building: "15"}
            but for complex structures it's not recommended.
            Better set value directly via javascript, e.g. 
            editable({
                value: {
                    city: "Moscow", 
                    street: "Lenina", 
                    building: "15"
                }
            });
          */ 
          return null;  
        },
      
       /**
        Converts value to string. 
        It is used in internal comparing (not for sending to server).
        
        @method value2str(value)  
       **/
       value2str: function(value) {
           return JSON.stringify(value);
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
          this.$inputs.each(function() {
            var parentSec = $(this).parents("div[name='configsection']");
            var section = parentSec.find('h2').text();
            if (!value.hasOwnProperty(section)) {
              value[section] = {};
            }
            $(this).val(value[section][$(this).attr('name')]);
          });
       },       
       
       /**
        Returns value of input.
        
        @method input2value() 
       **/          
       input2value: function() { 
          var value = {};
          this.$inputs.each(function() {
            var parentSec = $(this).parents("div[name='configsection']");
            var section = parentSec.find('h2').text();
            if (!value.hasOwnProperty(section)) {
              value[section] = {};
            }
            value[section][$(this).attr('name')] = $(this).val();
          });
          return value;
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
