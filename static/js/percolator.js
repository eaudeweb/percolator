
function displayAPIResponse(data, textStatus, jqXHR) {
    console.log(data);
    // $(".response").html(r.base);
}

function callTextAPI(data) {
    console.log(JSON.stringify( data ));
    $.ajax({
        url: '/tag',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify( data ),
        success: displayAPIResponse,
        error: function(){
            alert('error');
        }
    });
}

$(document).ready(function () {

    $('#textContent').keyup(function() {
          let max_text = 3000;
          let text_length = $(this).val().length;
          let text_remaining = max_text - text_length;
          if (text_remaining === max_text) {
              $('#textContentHelp').html(max_text + ' characters');
          } else {
              $('#textContentHelp').html(text_remaining + '/' + max_text + ' characters');
          }
    });


    $('#optionSourceText').change(function() {
      if ($(this).is(':checked')) {
         $('#lblSourceText').addClass('btn-primary').removeClass('btn-secondary');
         $('#lblSourceFile').addClass('btn-secondary').removeClass('btn-primary');
         $('#lblSourceURL').addClass('btn-secondary').removeClass('btn-primary');

         $('#textInputGroup').show();
         $('#fileInputGroup').hide();
         $('#urlInputGroup').hide();
      }
    });
    $('#optionSourceFile').change(function() {
      if ($(this).is(':checked')) {
         $('#lblSourceText').addClass('btn-secondary').removeClass('btn-primary');
         $('#lblSourceFile').addClass('btn-primary').removeClass('btn-secondary');
         $('#lblSourceURL').addClass('btn-secondary').removeClass('btn-primary');

         $('#textInputGroup').hide();
         $('#fileInputGroup').show();
         $('#urlInputGroup').hide();
      }
    });
    $('#optionSourceURL').change(function() {
      if ($(this).is(':checked')) {
         $('#lblSourceText').addClass('btn-secondary').removeClass('btn-primary');
         $('#lblSourceFile').addClass('btn-secondary').removeClass('btn-primary');
         $('#lblSourceURL').addClass('btn-primary').removeClass('btn-secondary');

         $('#textInputGroup').hide();
         $('#fileInputGroup').hide();
         $('#urlInputGroup').show();
      }
    });

});
