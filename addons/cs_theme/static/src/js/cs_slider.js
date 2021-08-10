(function () {
    'use strict';
    var instance = openerp;
    var website = openerp.website;
    var _t = openerp._t;

    // Actualizar la etiqueta de valores.
    $('.slider-input').on('input',function() {
      var newval=$(this).val();
      var $sliderContainer = $(this).parent();
      var $sliderValue = $sliderContainer.find(".slider-value");
      $sliderValue.text(newval);
    });

    $('input[type=range]#filter_price').on('change',function() {
      var value=$(this).val();
      console.log("Max price: " + value);
      instance.jsonRpc("/shop/filter", 'call', {'filter_type': 'price', 'value': value}).then(function (res) {
          var reload = res.reload
          if(reload) {
              location.reload(res);
          }
      });
    });


})();
