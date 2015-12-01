function getCookie(name) {
  var cookieValue = null;
  if (document.cookie && document.cookie != '') {
    var cookies = document.cookie.split(';');
    for (var i = 0; i < cookies.length; i++) {
      var cookie = jQuery.trim(cookies[i]);
      console.log("cookie_value: " + cookie)
      if (cookie.substring(0, name.length + 1) == (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        console.log("result: " + cookieValue)
        break;
      }  
    }
  }
  return cookieValue;  
}

function csrfSafeMethod(method) {
  return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

status_timeout_id = 0;

function status_message(json) {
  if (json["wait_status"] == "prepare") {
    return "Тест с id=" + json["session"] + " готовится к запуску.";
  }
  if (json["wait_status"] == "finished") {
    return "Тест с id=" + json["session"] + " выполняется.";
  }
  if (json["wait_status"] == "") {
    return "Тест с id=" + json["session"] + " завершен.";
  }
  console.log("wait_status: '" + json["wait_status"] + "'");
  return "";
}


function statusTest(row_id) {
  var path = $("td#name_" + row_id).html();
  $.ajax({
    url: "/status_test/",
    type: "POST",
    dataType: "json",
    data: {          
      tsid: row_id
    },
    error: function(json) {
      $("p#status").html("Status: " + json.status) 
    },
    success: function(json) {
      console.log("success(statusTest): json = " + JSON.stringify(json))
      $("td#status_" + row_id).html(status_message(json)); 
      var wr_but = $("input[type=button]#" + row_id).get(0);
      if (json["run_status"] == "0") {
        if (status_timeout_id) {
          clearTimeout(status_timeout_id);
        }
        var wr_but = $("input[type=button]#" + row_id).get(0);
        console.log("Button: " + wr_but);
        $(wr_but).attr("run_test", "Off");
        $(wr_but).attr("value", "Запустить");
      }
      else {
        status_timeout_id = 
          setTimeout(function() {
            console.log("setTimeout handler: status_test");
            statusTest(row_id, json);
        }, 3000);
        $(wr_but).attr("run_test", "On");
        $(wr_but).attr("value", "Остановить");
      }
    }
  });
}


function pollServers() {
  $.ajax({
    url: "/poll_servers/",
    type: "POST",
    dataType: "json",
    data: {},
    error: function(json) {
      $("p#status").html("Status: " + json.status) 
    },
    success: function(json) {
      console.log("JSON: " + JSON.stringify(json))
      $.each(json, function(tsid, el) {
        console.log("Key: " + tsid + ". Value: " + el["session"] + ".");
        $("td#status_" + tsid).html(status_message(el)); 
        var wr_but = $("input[type=button]#" + tsid).get(0);
        if (el["run_status"] == "0") {
          if (status_timeout_id) {
            clearTimeout(status_timeout_id);
          }
          var wr_but = $("input[type=button]#" + tsid).get(0);
          console.log("Button: " + wr_but);
          $(wr_but).attr("run_test", "Off");
          $(wr_but).attr("value", "Запустить");
        }
        else {
          status_timeout_id = 
            setTimeout(function() {
              console.log("setTimeout handler: status_test");
              statusTest(tsid, el);
          }, 3000);
          $(wr_but).attr("run_test", "On");
          $(wr_but).attr("value", "Остановить");
        }
      });
    }
  });
}



$(function() {  
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
      }
    }
  });
  var buts = $("input[type=button]");
  console.log("Size: " + buts.size());
  pollServers();
  $(buts).each(function() {
    $(this).bind("click", function(event) {
      var tr_id = this.id;
      var cur_action = $(this).attr("run_test");
      var wr_item = this;
      if (cur_action == "On") {
        if (status_timeout_id) {
          clearTimeout(status_timeout_id);
        }
        $.ajax({
          url: "/stop_test/",
          type: "POST",
          dataType: "json",
          data: {          
            tsid: wr_item.id
          },
          error: function(json) {
            console.log("Error Handler");
            $("p#status").html("Status: " + JSON.stringify(json));
          },
          success: function(json) {
            console.log("Test STOPPED.");
            $("td#status_" + tr_id).html("");
            $(wr_item).attr("run_test", "Off");
            $(wr_item).attr("value", "Запустить");
          }
        });
      } else {
        $.ajax({
          url: "/run_test/",
          type: "POST",
          dataType: "json",
          data: {          
            tsid: wr_item.id 
          },
          error: function(json) {
            console.log("Error Handler");
            $("p#status").html("Status: " + JSON.stringify(json));
          },
          success: function(json) {
            statusTest(wr_item.id, json);
          }
        });
      }
    });
  });
});
