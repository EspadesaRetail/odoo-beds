"use strict";
(function ($) {
    $("#beds_cookie_accept").click(function(event){
        event.preventDefault();
        $(".cc-cookies").addClass("hidden");
        $.ajax($(event.target).attr("href"), {
            "complete": function(jqXHR, textStatus){
                $(event.target).closest(".cc-cookies").hide("fast");
            }
        });
    });
})(jQuery);
