function displayAPIResponse(response, textStatus, jqXHR) {

    let updateResultsCard = function (results, list, badge) {
        let count = Object.keys(results).length;
        badge.text(count);
        if (jQuery.isEmptyObject(results)) {
            list.append($("<li class='list-group-item'>").html("<i>No results</i>"));
        }
        else {
            for (let key in results) {
                if (results.hasOwnProperty(key)) {
                    if ($('#checkboxScores').is(':checked')) {
                        list.append($("<li class='list-group-item d-flex justify-content-between align-items-center'>").html(
                            key + "<span class='badge badge-primary badge-pill'>" + results[key].toFixed(2) + "</span>"
                        ));
                    }
                    else {
                        list.append($("<li class='list-group-item'>").text(key));
                    }
                }
            }
        }
        list.parent().parent().show();
    };
    console.log(response);
    let speciesplus_list = $('#speciesplusList');
    let countries_list = $('#countriesList');
    let speciesplus_badge = $('#speciesplusBadge');
    let countries_badge = $('#countriesBadge');

    speciesplus_list.empty();
    countries_list.empty();

    if (response.hasOwnProperty('speciesplus')) {
        updateResultsCard(response['speciesplus'], speciesplus_list, speciesplus_badge);
    }

    if (response.hasOwnProperty('countries')) {
        updateResultsCard(response['countries'], countries_list, countries_badge);
    }

    $('.load-spinner').modal('hide');
}


$(document).ready(function () {

    $('#textSource').keyup(function () {
        let max_text = 3000;
        let text_size = $(this).val().length;
        if (text_size === 0) {
            $('#textContentHelp').html(max_text + ' characters');
            $('#btnSubmit').attr('disabled', true);
        } else {
            $('#textContentHelp').html(text_size + '/' + max_text + ' characters');
            $('#btnSubmit').attr('disabled', false);
        }
    });


    $('#optionSourceText').change(function () {
        if ($(this).is(':checked')) {
            $('#lblSourceText').addClass('btn-primary').removeClass('btn-secondary');
            $('#lblSourceFile').addClass('btn-secondary').removeClass('btn-primary');
            $('#lblSourceURL').addClass('btn-secondary').removeClass('btn-primary');

            $('#textSource').val('');
            $('#textInputGroup').show();
            $('#fileInputGroup').hide();
            $('#urlInputGroup').hide();
            $('#btnSubmit').attr('disabled', true);
        }
    });
    $('#optionSourceFile').change(function () {
        if ($(this).is(':checked')) {
            $('#lblSourceText').addClass('btn-secondary').removeClass('btn-primary');
            $('#lblSourceFile').addClass('btn-primary').removeClass('btn-secondary');
            $('#lblSourceURL').addClass('btn-secondary').removeClass('btn-primary');

            let inputFile = $('#fileSource');
            inputFile.val('');
            inputFile.next('.custom-file-label').text('Choose file');

            $('#textInputGroup').hide();
            $('#fileInputGroup').show();
            $('#urlInputGroup').hide();
            $('#btnSubmit').attr('disabled', true);
        }
    });
    $('#optionSourceURL').change(function () {
        if ($(this).is(':checked')) {
            $('#lblSourceText').addClass('btn-secondary').removeClass('btn-primary');
            $('#lblSourceFile').addClass('btn-secondary').removeClass('btn-primary');
            $('#lblSourceURL').addClass('btn-primary').removeClass('btn-secondary');

            $('#urlSource').val('');
            $('#textInputGroup').hide();
            $('#fileInputGroup').hide();
            $('#urlInputGroup').show();
            $('#btnSubmit').attr('disabled', true);
        }
    });

    $('#fileSource').on('change', function () {
        let fileName = $(this).val();
        $(this).next('.custom-file-label').html(fileName);
        if (fileName.length === 0) {
            $('#btnSubmit').attr('disabled', true);
        }
        else {
            $('#btnSubmit').attr('disabled', false);
        }
    });

    $('#urlSource').keyup(function () {
        if ($(this).val().length === 0) {
            $('#btnSubmit').attr('disabled', true);
        }
        else {
            $('#btnSubmit').attr('disabled', false);
        }
    });



    $('#formTag').submit(function(e) {
      e.preventDefault();
      let domains = $('#selectDomains option:selected').map(function(){ return this.value }).get();
      $('#hiddenDomains').val(domains.join(','));
      let form_data = new FormData($(this)[0]);
      let url = $(this).attr('action');
      $('#speciesplusCard').hide();
      $('#countriesCard').hide();
      $('.load-spinner').modal('show');
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
