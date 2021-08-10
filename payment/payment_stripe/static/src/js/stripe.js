/*
 * Conexflow
 * 
 */
var userEdition = false;

$(document).ready(function () {

    var instance = openerp;


    $('.js_payment').each(function () {

        var total_amount = parseFloat($("input[id='internal_amount']").val());
        var pg = parseFloat($("input[id='internal_percentage']").val());
        
        var partial_amount = (total_amount * (1 - pg)).toFixed(0);

        var check = $("input[name='check_partial_pay']");
        var field_amount = $("input[name='CF_Amount']");
        var set_partial_amount = $("input[name='CF_SetPartialAmount']");

        
        $(check).change(function () {
            if ($(this).is(":checked")) {
                $(field_amount).val(partial_amount);
                $(set_partial_amount).val(1);
            } else {
                $(field_amount).val(total_amount);
                $(set_partial_amount).val(0);
            }

        });

        

        

    });
});
