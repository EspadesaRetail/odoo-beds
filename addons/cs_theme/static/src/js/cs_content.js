(function () {
    'use strict';

    /*
     var website = openerp.website;
     website.contentMenu = {};
     website.add_template_file('/website/static/src/xml/website.contentMenu.xml');
     var _t = openerp._t;
     */

    var instance = openerp;
    var website = openerp.website;
    website.add_template_file('/cs_theme/static/src/xml/cs_content.xml');
    var _t = openerp._t;
    var _lt = openerp._lt;
    var QWeb = openerp.qweb;


    website.Bubbles = openerp.Class.extend({
        init: function (container, html) {
            var self = this;
            var bb = $('#bb')

            var position;
            var $container = $(container);

            position = $('body').offset();
            var pt = $(window).scrollTop() + position.top + "px";
            var pl = position.left + "px";

            pt = $container.offset().top - 210 + "px";
            pl = $container.offset().left - (175 - ($container.width()) / 2) + "px";


            bb.css({
                'position': 'absolute',
                'top': pt,
                'left': pl,
                'z-index': '1000;'

            });

            $('#bb-text').html(html);
            var self = this;
            bb.show();

        },
        remove: function () {
            var self = this;
            $('#bb').hide();
        }
    });


    // Activar los globos en 7 coasas que bed's hace port ti.
    website.ready().done(function () {
        var bubble = null;
        $(document.body).on('mouseenter', 'div[data-action=cs_bubble]', function () {
            var $content, bn, id;
            var self = this
            bn = $(self).data("value");
            id = "#" + bn;
            $content = $(id);

            bubble = new website.Bubbles(self, $content.html());
        });

        $(document.body).on('mouseleave', 'div[data-action=cs_bubble]', function () {
            bubble.remove();
            bubble = null;
        });

    });

    /* Permite cambiar como se ve la lista de productos */
    $('.js_session').on("click", function (event) {
        var opt = $(event.target).closest("li").find('i');

        var grid = true;
        if ($(opt).hasClass('fa-th-list')) {
            grid = false;
        }

        openerp.jsonRpc("/shop/grid", 'call', {'grid': grid}).then(function (res) {

            var reload = res.reload

            if(reload) {
                location.reload(res);
            }
        });
    });


})();









jQuery(document).ready(function ($) {

    $('#product-carousel').carousel({
        interval: 5000
    });

    $('#carousel-text').html($('#slide-content-0').html());

    //Handles the carousel thumbnails
    $('[id^=carousel-selector-]').click(function () {
        var id = this.id.substr(this.id.lastIndexOf("-") + 1);
        var id = parseInt(id);
        $('#product-carousel').carousel(id);
    });


    // When the carousel slides, auto update the text
    $('#product-carousel').on('slid.bs.carousel', function (e) {
        var id = $('.item.active').data('slide-number');
        $('#carousel-text').html($('#slide-content-' + id).html());
    });
});
