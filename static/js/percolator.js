function displayAPIResponse(response, textStatus, jqXHR) {

    let updateResultsCard = function(resultsList, results) {
        resultsList.empty();
        for (let key in results) {
            if (results.hasOwnProperty(key)) {
                resultsList.append($("<li class='list-group-item'>").text(key));
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


function callTextAPI(data) {
    $.ajax({
        url: '/tag',
        type: 'POST',
        contentType: 'application/json',
        dataType: 'json',
        data: JSON.stringify(data),
        success: displayAPIResponse,
        error: function () {
            alert('error');
        }
    });
}


function makeJSONPayload(domains = '', text, constant_score = true) {
    return {
        'domains': domains,
        'constant_score': constant_score,
        'text': text
    }
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

    $('#inputGroupFile').on('change',function(){
        let fileName = $(this).val();
        $(this).next('.custom-file-label').html(fileName);
    });

    $('#btnSubmit').click(function () {
        let domains = [];
        $("#selectDomains :selected").each(function () {
            domains.push($(this).val());
        });
        let constant_score = $('#checkboxScores').is(':checked');
        let text = $('#textContent').val();
        let payload = makeJSONPayload(domains, text, constant_score);
        $('#speciesplusCard').hide();
        $('#countriesCard').hide();
        // let spinner = $('.load-spinner');
        // spinner.modal('show');
        callTextAPI(payload);
    });

});
