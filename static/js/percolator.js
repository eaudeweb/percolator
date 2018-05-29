function displayAPIResponse(response, textStatus, jqXHR) {

    let updateResultsCard = function (resultsList, results) {
        resultsList.empty();
        for (let key in results) {
            if (results.hasOwnProperty(key)) {
                if ($('#checkboxScores').is(':checked')) {
                    resultsList.append($("<li class='list-group-item d-flex justify-content-between align-items-center'>").html(
                        key + "<span class='badge badge-primary badge-pill'>" + results[key].toFixed(2) + "</span>"
                    ));
                }
                else {
                    resultsList.append($("<li class='list-group-item'>").text(key));
                }
                console.log(key + " -> " + results[key]);
            }
        }

        resultsList.parent().parent().show();
    };
    console.log(response);
    if (response.hasOwnProperty('speciesplus')) {
        updateResultsCard($('#speciesplusList'), response['speciesplus']);
    }

    if (response.hasOwnProperty('countries')) {
        updateResultsCard($('#countriesList'), response['countries']);
    }

    // $('.load-spinner').on('shown.bs.modal', function (e) {
    //     $('.load-spinner').modal('hide');
    // });
}


$(document).ready(function () {

    $('#textContent').keyup(function () {
        let max_text = 3000;
        let text_length = $(this).val().length;
        let text_remaining = max_text - text_length;
        if (text_remaining === max_text) {
            $('#textContentHelp').html(max_text + ' characters');
        } else {
            $('#textContentHelp').html(text_remaining + '/' + max_text + ' characters');
        }
    });


    $('#optionSourceText').change(function () {
        if ($(this).is(':checked')) {
            $('#lblSourceText').addClass('btn-primary').removeClass('btn-secondary');
            $('#lblSourceFile').addClass('btn-secondary').removeClass('btn-primary');
            $('#lblSourceURL').addClass('btn-secondary').removeClass('btn-primary');

            $('#textInputGroup').show();
            $('#fileInputGroup').hide();
            $('#urlInputGroup').hide();
        }
    });
    $('#optionSourceFile').change(function () {
        if ($(this).is(':checked')) {
            $('#lblSourceText').addClass('btn-secondary').removeClass('btn-primary');
            $('#lblSourceFile').addClass('btn-primary').removeClass('btn-secondary');
            $('#lblSourceURL').addClass('btn-secondary').removeClass('btn-primary');

            $('#textInputGroup').hide();
            $('#fileInputGroup').show();
            $('#urlInputGroup').hide();
        }
    });
    $('#optionSourceURL').change(function () {
        if ($(this).is(':checked')) {
            $('#lblSourceText').addClass('btn-secondary').removeClass('btn-primary');
            $('#lblSourceFile').addClass('btn-secondary').removeClass('btn-primary');
            $('#lblSourceURL').addClass('btn-primary').removeClass('btn-secondary');

            $('#textInputGroup').hide();
            $('#fileInputGroup').hide();
            $('#urlInputGroup').show();
        }
    });

    $('#inputGroupFile').on('change', function () {
        let fileName = $(this).val();
        $(this).next('.custom-file-label').html(fileName);
    });

    $('#formTag').submit(function(e) {
      e.preventDefault();
      let domains = $('#selectDomains option:selected').map(function(){ return this.value }).get();
      $('#domains').value = domains.join(',');
      let form_data = new FormData($(this)[0]);
      let url = $(this).attr('action');
      $('#speciesplusCard').hide();
      $('#countriesCard').hide();
      // let spinner = $('.load-spinner');
      // spinner.modal('show');
      $.ajax({
          type:'POST',
          url: url,
          processData: false,
          contentType: false,
          cache: false,
          data : form_data,
          success: displayAPIResponse
      });
    });
});
