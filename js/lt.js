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

$(function() {
  var buts = $("input[type=button]");
  console.log("Size: " + buts.size());
  $(buts).each(function() {
    $(this).bind("click", function(event) {
      console.log("Button: " + this.id);
      a = "td#" + this.id;
      console.log("a: " + a);
      config_cell = $(a)[0];
      console.log("Path Number: " + config_cell.html());
      if ($(this).attr("run_test") == "On") {
        $(this).attr("run_test", "Off");
        $(this).attr("value", "Запустить");
      } else {
        $(this).attr("run_test", "On");
        $(this).attr("value", "Остановить");
      }
      var csrftoken = getCookie('csrftoken');
      $.ajaxSetup({
        beforeSend: function(xhr, settings) {
          if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
          }
        }
      });

      $.ajax({
        url: "/tests/",
        type: "POST",
        dataType: "json",
        data: {          
          ini_path: "test"
          // csrfmiddlewaretoken: "{{ csrf_token }}"
        },
        success: function(json) {
          $("#result").html(json.server_response);
        },
        error: function(xhr, errmsg, err) {
          alert(xhr.status + ": " + xhr.responseText)
        }
      });
    });
  });
});
