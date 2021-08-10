(function () {
  'use strict';
  var website = openerp.website;

  $('.oe_website_sale #add_to_cart, .oe_website_sale #products_grid .a-submit')
  .off('click')
  .removeClass('a-submit')
  .click(function (event) {

    // Gestión de la ventana modal de localización.
    var zip = $('#input_zip_code').val();
    if(zip==null || zip.length != 5) {



      var $form = $(this).closest('form');
      event.preventDefault();
      openerp.jsonRpc("/location/modal", 'call', {}).then(function (modal) {
        var $modal = $(modal);

        $modal.appendTo($form)
        .modal()
        .on('hidden.bs.modal', function () {
          $(this).remove();
        });

        // Aceptar
        $modal.on('click', '.a-submit', function () {
          var zip_code = $modal.find('#input_zip_code').val();
          openerp.jsonRpc("/shop/set_zip_code", 'call', {'zip_code': zip_code})
          .then(function (data) {
            console.log("ACEPTAR CODIGO POSTAL");
            console.log(data);
            console.log(data.zip_code);
            console.log(data.zip_code_state);

            $('input#zip_code').val(data.zip_code);
            $('#input_zip_code').val(data.zip_code);
            $('#zip_code_state').text(data.zip_code_state);
            $modal.modal('hide');
          });
        });

        // Volver
        $modal.on('click', '.a-cancel', function () {
          $modal.modal('hide');
        });
      }


    });

  });



  website.if_dom_contains('#set_location,#show_location', function () {
    function set_zip_code(openerp, zip) {
      openerp.jsonRpc("/shop/set_zip_code", 'call', {'zip_code': zip})
      .then(function (data) {
        window.location.reload();
      });
    }

    function postalCodeLookup(pos) {
      var fallback = setTimeout(function () {
        fail('10 seconds expired');
      }, 10000);

      clearTimeout(fallback);
      var point = new google.maps.LatLng(pos.coords.latitude, pos.coords.longitude);
      new google.maps.Geocoder().geocode({'latLng': point}, function (res, status) {
        if (status == google.maps.GeocoderStatus.OK && typeof res[0] !== 'undefined') {
          var zipcode = "";
          for(var j=0;j < res[0].address_components.length; j++){
            for(var k=0; k < res[0].address_components[j].types.length; k++){
              if(res[0].address_components[j].types[k] == "postal_code"){
                zipcode = res[0].address_components[j].short_name;
              }
            }
          }
          set_zip_code(openerp, zipcode);
        } else {
          fail('Unable to look-up geolocation');
        }
      });
      function fail(err) {
        console.log('err', err);
      }
    }


    $('#search_zip_code').click(function(ev) {
      if (navigator.geolocation) {
        var startPos;
        var geoSuccess = function(pos) {
          postalCodeLookup(pos);
        };
        navigator.geolocation.getCurrentPosition(geoSuccess);
      }
    });

    $('#input_zip_code').keyup( function (e) {
      if (e.keyCode == 13) {
        var zip = $('#input_zip_code').val();
        set_zip_code(openerp,zip);
        e.preventDefault();
      }
    });
    $('#get_zip_code').click(function(ev) {
      var zip = $('#input_zip_code').val();
      set_zip_code(openerp, zip);
    });

    // Recargar cuando se resetea la localización.
    $('#location_reset').click(function(){
      openerp.jsonRpc("/location/js_reset", 'call', {})
      .then(function (data) {
        window.location.reload();
      });
    });
  });

  /*
  Aplicar restricciones por área al contenido.
  Una vez añadido un contenido a una página, se puede especificar la restricción a la que está sujeta.
  */
  function restricted_area(zip_code) {
    // Ocultar todo el contenido y luego mostrar el que convenga.
    $("[class~='restricted-area-peninsula']").each(function(index) {
      $(this).addClass("restricted-no-display");
    });
    $("[class~='restricted-area-baleares']").each(function(index) {
      $(this).addClass("restricted-no-display");
    });
    $("[class~='restricted-area-all']").each(function(index) {
      $(this).addClass("restricted-no-display");
    });

    if(zip_code==null) {
      $("[class~='restricted-area-all']").each(function(index) {
        $(this).removeClass("restricted-no-display");
      });
      return
    }

    var area_code = zip_code.toString().substring(0,2);

    // Mostrar en peninsula.
    if(area_code != '07') {
      $("[class~='restricted-area-peninsula']").each(function(index) {
        $(this).removeClass("restricted-no-display");
      });
      return;
    }

    if(area_code == '07') {
      $("[class~='restricted-area-baleares']").each(function(index) {
        $(this).removeClass("restricted-no-display");
      });
      return;
    }

  }
  restricted_area($('#zip_code').data('zip-code'));


})();
