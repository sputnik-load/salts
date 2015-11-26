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
  return "";
}


function initStatusTest(row_id) {
  console.log("Defining of statuses.");
  var path = $("td#name_" + row_id).html();
  $.ajax({
    url: "/init_status_test/",
    type: "POST",
    dataType: "json",
    data: {          
      ini_path: path
    },
    error: function(json) {
      $("p#status").html("Status: " + json.status) 
    },
    success: function(json) {
      console.log("Console: " + JSON.stringify(json));
      console.log("Function initStatusTest: success handler");
      console.log("Status Test: " + json["run_status"]);
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



function statusTest(row_id, json_obj) {
  console.log("statusTest: row_id: " + row_id);
  // console.log("statusTest: json_obj: " + JSON.stringify(json_obj));
  $.ajax({
    url: "/status_test/",
    type: "POST",
    dataType: "json",
    data: {          
      ini_path: json_obj["ini_path"],
      wait_status: json_obj["wait_status"],
      session: json_obj["session"]
    },
    error: function(json) {
      console.log("Error Handler")
      $("p#status").html("Status: " + json.status) 
    },
    success: function(json) {
      console.log("Function statusTest: success handler");
      $("td#status_" + row_id).html(status_message(json)); 
      if (json["wait_status"] == "") {
        if (status_timeout_id) {
          clearTimeout(status_timeout_id);
        }
        $(wr_item).attr("run_test", "Off");
        $(wr_item).attr("value", "Запустить");
      }
      else {
        status_timeout_id = 
          setTimeout(function() {
            console.log("setTimeout handler: status_test");
            statusTest(row_id, json);
        }, 3000);
      }
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
  $(buts).each(function() {
    initStatusTest(this.id);
    $(this).bind("click", function(event) {
      /* 
      var csrftoken = getCookie('csrftoken');
      $.ajaxSetup({
        beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
        }
      });
      */
      var running_ini_path = $("td#name_" + this.id).html();
      var tr_id = this.id;
      var cur_action = $(this).attr("run_test");
      var wr_item = this;
      console.log("PATH: " + running_ini_path);
      if (cur_action == "On") {
        if (status_timeout_id) {
          clearTimeout(status_timeout_id);
        }
        $.ajax({
          url: "/stop_test/",
          type: "POST",
          dataType: "json",
          data: {          
            ini_path: running_ini_path
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
            ini_path: running_ini_path
          },
          error: function(json) {
            console.log("Error Handler");
            $("p#status").html("Status: " + JSON.stringify(json));
          },
          success: function(json) {
            console.log("Function bind_click: success handler");
            var msg = "Тест с id=" + json["session"] + " готовится к запуску.";
            $("td#status_" + tr_id).html(msg);
            status_timeout_id = 
              setTimeout(function() {
                console.log("setTimeout handler: run_test");
                statusTest(wr_item.id, json);
              }, 3000);
            $(wr_item).attr("run_test", "On");
            $(wr_item).attr("value", "Остановить");
          }
        });
      }
    });
  });
});
