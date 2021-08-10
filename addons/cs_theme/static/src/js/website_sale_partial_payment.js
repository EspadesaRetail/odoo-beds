/* 
 * Este script reemplaza el módulo estándar que hay en website_sale/static/src/js/website_sale_payment.js
 * Se necesita para añadir la posibilidad de gestinar pagos parciales.
 */

$(document).ready(function () {

    // When choosing an acquirer, display its Pay Now button
    var $check_partial_payment = $("input[name='check_partial_pay']");

    $check_partial_payment.on("change", function (ev) {
        ev.preventDefault();
        ev.stopPropagation();
        set_partial_payment = false;
        if ($check_partial_payment.is(":checked")) {
            set_partial_payment = true;
        }

        openerp.jsonRpc('/shop/payment/partial/', 'call', {'set_partial_payment':set_partial_payment}).then(function (data) {
            console.log(data);
        });
    });

});
