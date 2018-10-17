// preload image function
function preload(arrayOfImages) {
    $(arrayOfImages).each(function () {
        $('<img/>')[0].src = this;
    });
}

$(document).ready(function () {

    // set up radio boxes
    $('.radioholder').each(function () {
        $(this).children().hide();
        var description = $(this).children('label').html();
        $(this).append('<span class="desc">' + description + '</span>');
        $(this).prepend('<span class="tick"></span>');
        // on click, update radio boxes accordingly

        $(this).click(function () {
            $(this).children('input').prop('checked', true);
            $(this).children('input').trigger('change');

            if ($(this).children('input').val() === 'net_range') {
                $('#ip-testing').show();
                $('#ip-testing-1').hide();
                $('#ip-testing-2').hide();
            }
            else if ($(this).children('input').val() === 'ip_range') {
                $('#ip-testing-1').show();
                $('#ip-testing').hide();
                $('#ip-testing-2').hide();
            }
            else if ($(this).children('input').val() === 'add') {
                $('#ip-testing-2').show();
                $('#ip-testing-1').hide();
                $('#ip-testing').hide();
            }

        });
    });
    // update radio holder classes when a radio element changes
    $('input[type=radio]').change(function () {
        $('input[type=radio]').each(function () {
            if ($(this).prop('checked') == true) {
                $(this).parent().addClass('activeradioholder');
            }
            else $(this).parent().removeClass('activeradioholder');
        });
    });
    // manually fire radio box change event on page load
    $('input[type=radio]').change();

    // set up select boxes
    $('.selectholder').each(function () {
        $(this).children().hide();
        var description = $(this).children('label').text();
        $(this).append('<span class="desc">' + description + '</span>');
        $(this).append('<span class="pulldown"></span>');


    });
});

