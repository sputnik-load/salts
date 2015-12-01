
function edit_tbl_handler() {
  var table = document.getElementById("edit");
  for (var i = 0; i < table.tBodies[0].rows.length; i++) {
    var row = table.tBodies[0].rows[i];
    row.onclick = onRowClick;
  }
/*
  var tbl = $("#edit");
  console.log("Tbl Size: " + tbl.size());
  $(tbl).each(function() {
    console.log("Table T");
    $(this).on("click", "td", function() {
        console.log("Row Click.");
        $(this).html("<input data-type='text' type='text'></>");
        $("input[type=text]").focus();

    })
  })
*/

  function onRowClick(event) {
    console.log("On Row Click");
    var target = event ? event.target : window.event.srcElement;
    this.onclick = null;
    this.className = 'editable';
    for (var i = 0; i < this.cells.length; i++) {
      var cell = this.cells[i];
      var input = document.createElement('input');
      input.setAttribute('type', cell.getAttribute('data-type') || 'text');
      input.value = cell.firstChild.data;
      cell.replaceChild(input, cell.firstChild);
      if (cell == target)
         input.focus();
    }
  }

}


$(function() {
  console.log("Ready.")
  // $("#save-id").submit(function() {
  //  console.log("Append POST data.");
  //});

  // edit_tbl_handler();
})
