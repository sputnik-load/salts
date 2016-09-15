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

(function ($) {
    "use strict";
    
    var CustomData = function (options) {
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
           this.$input = this.$tpl.find('input');
        },
        
        /**
        Default method to show value in element. Can be overwritten by display option.
        
        @method value2html(value, element) 
        **/
        value2html: function(value, element) {
            if(!value) {
                $(element).empty();
                return; 
            }
            var html = $('<div>').text(value.testname).html();
            $(element).html(html); 
        },
        
        /**
        Gets value from element's html
        
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
           var str = '';
           if(value) {
               for(var k in value) {
                   str = str + k + ':' + value[k] + ';';  
               }
           }
           return str;
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
           this.$input.filter('[name="testname"]').val(value.testname);
           this.$input.filter('[name="duration"]').val(value.duration);
       },       
       
       /**
        Returns value of input.
        
        @method input2value() 
       **/          
       input2value: function() { 
           return {
              testname: this.$input.filter('[name="testname"]').val(), 
              duration: this.$input.filter('[name="duration"]').val(), 
           };
       },        
       
        /**
        Activates input: sets focus on the first field.
        
        @method activate() 
       **/        
       activate: function() {
            this.$input.filter('[name="testname"]').focus();
       },  
       
       /**
        Attaches handler to submit form in case of 'showbuttons=false' mode
        
        @method autosubmit() 
       **/       
       autosubmit: function() {
           this.$input.keydown(function (e) {
                if (e.which === 13) {
                    $(this).closest('form').submit();
                }
           });
       }       
    });

    CustomData.defaults = $.extend({}, $.fn.editabletypes.abstractinput.defaults, {
        tpl: "<div class='editable-customdata'>" +
             "<label><span>Имя теста: </span>" +
             "<input type='text' name='testname'>" +
             "</label></div>" +
             "<div class='editable-customdata'>" +
             "<label><span>Длительность (сек): </span>" +
             "<input type='number' name='duration'>" +
             "</label></div>", 
        inputclass: ""
    });

    $.fn.editabletypes.customdata = CustomData;

}(window.jQuery));
