/*
 * Búsqueda mediante pantalla completa.
 * Ver layout.xml
 *
 */
var userEdition = false;

function openSearch() {
    document.getElementById("custom_search").style.height = "100%";
    setTimeout(function () {
        $('#custom_search_input').text("");
        $('#custom_search_input').focus();
        $('#custom_search_input').select();
    }, 100);
}

function closeSearch() {
    if (!userEdition) {
        document.getElementById("custom_search").style.height = "0%";
    }
}

function startEdition() {
    userEdition = true;
}
function endEdition() {
    userEdition = false;
}


function cs_keypress(event) {
    if (event.keyCode == 13) {
        userEdition = false;
        closeSearch();
    }
}

function cs_search_onClick(event) {
    console.log("search_oncliclk");
    window.location.href = "/shop?search=" + $('#custom_search_input').val();

}


function cs_keyup(event) {
    if (event.keyCode == 27) {
        userEdition = false;
        closeSearch();
    }
}

/* Aumentar el tamaño del texto bed's */
$("span").filter(function() {
    return $(this).text() === "bed's";
}).css("font-size", "18px");

$(document).ready(function () {

    /* Custom chat */
    /* Hace que al pulsar sobre el icono de chat de la cabecera, se active el chat. */
    $('li.custom-chat,p.pie-chat').each(function () {
        var custom_chat = this;
        $(custom_chat).click(function (ev) {
            var chat = $('div.oe_chat_button');
            if ( chat.length ) {
              chat.click();
            } else {
              window.location.href = "/form/contactar";
            }

        });

    });



    $('.custom-search').each(function () {
        var cs_search = this;
    });


    /* Auto zoom full page */
    $('.cs-auto-zoom').each(function () {
        var cs_auto_zoom = this;

        $(cs_auto_zoom).on('click', 'img.cs-img-zoom', function (ev) {
            var $img = $(ev.target);
            var src = $img.attr('src');

            var $p = $img.parent();
            var $carousel = $p.parent();

            // Selected slide.
            var slide = $p.data('slide-number');

            var images = $carousel.find("img.cs-img-zoom");

            $img = $(images[slide]);

            //console.log("Auto zoom");

            $('body').each(function () {
                var $h = $('<div id="id_auto_zoom" class="cs-auto-zoom-view"> \
                              <span class="cs-button-close">×</span><img class="cs-img-auto-zoom" src=""></img> \
                              <div class="cs-zoom-left"><i class="fa fa-chevron-left" style="font-size:25px;"></i></div>\
                              <div class="cs-zoom-right"><i class="fa fa-chevron-right" style="font-size:25px;"></i></div>\
                            </div>');
                $(this).append($h);

                // Close de zoom.
                $h.find('.cs-img-auto-zoom,.cs-button-close').on('click', function (ev) {
                    $h.detach();
                });

                // Al hacer el scroll en la página, también se cierra.
                $( window ).scroll(function() {
                      $h.detach();
                      $( window ).unbind('scroll');
                });

                var $img_auto_zoom = $h.find(".cs-img-auto-zoom");
                $h.find('.cs-zoom-left').on('click', function (ev) {
                    slide--;
                    if(slide < 0) slide = images.length-1;
                    $img = $(images[slide]);
                    src = $img.attr('src');
                    $img_auto_zoom.attr("src", src);
                });

                $h.find('.cs-zoom-right').on('click', function (ev) {
                    slide++;
                    if(slide >= images.length) slide=0;
                    $img = $(images[slide]);
                    src = $img.attr('src');
                    $img_auto_zoom.attr("src", src);
                });


                src = $img.attr('src');
                $img_auto_zoom.attr("src", src);

                redim($img_auto_zoom);
            });

        });


        /* Redimensiona una imagen */
        function redim(img) {

            var maxWidth = $(window).width();     // Max width for the image
            var maxHeight = $(window).height();   // Max height for the image

            if (maxWidth > maxHeight) {
              maxHeight = maxHeight * 0.95;
              maxWidth = maxWidth * 0.8;
            } else {
              maxHeight = maxHeight * 0.8;
              maxWidth = maxWidth * 0.95;
            }

            var ratio = 0;                              // Used for aspect ratio
            var width = $(img).width();                 // Current image width
            var height = $(img).height();               // Current image height

            ratiow = maxWidth / width;   // get ratio for scaling image
            ratioh = maxHeight / height; // get ratio for scaling image

            // Check if the current width is larger than the max
            if (width > maxWidth && height > maxHeight) {
                ratiow = maxWidth / width;
                ratioh = maxHeight / height;

              } else if (width > maxWidth && height <= maxHeight) {
                ratiow = maxWidth / width;

              } else if (width <= maxWidth && height > maxHeight) {
                ratioh = maxHeight / height;

              }

            ratio = ratiow;
            if(ratioh < ratiow) {
              ratio = ratioh;
            }

            height = height * ratio;
            width = width * ratio;

            $(img).css("width", width);
            $(img).css("height", height);

            var top = ($(window).height() - height) / 2;
            var left = ($(window).width() - width) / 2;

            $(img).css("top", top);
            $(img).css("left", left);

        }

    });



    /* Los mejores precios del mercado */
    /* Añadir un enlace cuando se introduce un sello de los mejores precios del mercado */
    $('div.sello-mejor-precio').each(function () {
        var sello = this;

        // get row parent.
        var p = $(sello).parents()[0];

        $(p).click(function (ev) {
            window.location.href = "/page/los-mejores-precios-del-mercado";
        });

        $(p).mouseover(function () {
            $(p).css('cursor', 'pointer');
        })
        $(p).mouseout(function () {
            $(p).css('cursor', 'default');
        });


    });



});
