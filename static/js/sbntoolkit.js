// Based on:
// http://stackoverflow.com/questions/14186565/jquery-hide-and-show-toggle-div-with-plus-and-minus-icon

$(document).ready(function(e) {

  $('#license').click(function(e){
    e.preventDefault();
    $("#license-text").slideToggle('slow');
    return false;
  });

  $("#license-text").hide()
  return false;
});
