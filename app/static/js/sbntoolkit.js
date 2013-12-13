$(document).ready(
    function () {
        "use strict";

        $('#license').click(function (e) {
            e.preventDefault();
            $("#license-text").slideToggle('slow');
            return false;
        });

        $("#license-text").hide();

        $(".inputform").submit(function (e) {

            e.preventDefault();

            var postData = $(this).serializeArray();

            $('#submit').attr('disabled', 'disabled');

            $.ajax({
                type: "POST",
                url: "/",
                data: postData,
                success: function (post_response) {
                    $('#submit').removeAttr('disabled');
                    $('#results-placeholder').hide().html(post_response).fadeIn(1500);
                }
            });

            return false;
        });

    }
);
