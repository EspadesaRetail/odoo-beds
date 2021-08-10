$(document).ready(function () {
    var product_packs;


    // Actualizar el precio total del pack.
    function update_pack_price(pack) {
        var $input;
        var $pack = pack;
        var $products = $pack.find('input.pack-product-id');

        var product_id;
        var bruto = 0;
        var neto = 0;
        var product_ids = [];
        $products.each(function (index) {
            product_id = $(this).attr('data-product-id');
            product_ids.push(+product_id);
            qty = Number.parseFloat($(this).attr('data-qty'));
            b = Number.parseFloat($(this).attr('data-product-list-price'));
            n = Number.parseFloat($(this).attr('data-product-price'));

            if(!Number.isNaN(qty) && !Number.isNaN(b) && !Number.isNaN(n)) {
                bruto = bruto + qty * b;
                neto = neto + qty * n;
            }
        });

        var value;
        var $precio = $pack.find('.pack-price').children('span');
        value = neto.toLocaleString('es-ES', {'maximumFractionDigits': 2, 'minimumFractionDigits': 2});
        $precio.text(value);

        var $ahorro = $pack.find('.pack-list-price').children('span');
        value = bruto - neto;
        value = value.toLocaleString('es-ES', {'maximumFractionDigits': 2, 'minimumFractionDigits': 2});
        $ahorro.text(value);
    }

    // Interacción con todos los packs.
    $('#product_packs').each(function () {
        product_packs = this;


        // Detectar un cambio en los atributos y obtener el product_id y los precios.
        $(product_packs).on('change', 'input.js_pack_variant_change, select.js_pack_variant_change', function (ev) {
            var $ul = $(ev.target).closest('.js_pack_change_product');
            var $pack = $ul.closest('.js_pack');
            var $parent = $ul.closest('.js_pack_product');
            var $product_id = $parent.find('input.pack-product-id').first();
            var variant_ids = $ul.data("attribute_value_ids");

            var values = [];
            $parent.find('input.js_pack_variant_change:checked, select.js_pack_variant_change').each(function () {
                values.push(+$(this).val());
            });

            var data_product_id = false;

            for (var k in variant_ids) {
                if (_.isEmpty(_.difference(variant_ids[k][1], values))) {
                    data_product_id = variant_ids[k];
                    break;
                }
            }

            // Activar la variante del color seleccionado.
            $('.css_attribute_color input', product_packs).on('change', function (ev) {
                $('.css_attribute_color').removeClass("active");
                $('.css_attribute_color:has(input:checked)').addClass("active");
            });

            if (data_product_id) {
                $product_id.attr('data-product-id', data_product_id[0])
                .attr('data-product-price', data_product_id[2])
                .attr('data-product-list-price', data_product_id[3]);
                update_pack_price($pack);
            }
        });

        // Seleccionar la primer variante de cada componente del pack.
        $('select.js_pack_variant_change').trigger('change');
        $('input.js_pack_variant_change').attr('checked', true).trigger('click');



        // Añadir el pack al carrito.
        $(product_packs).on('click', 'a.js_add_pack_to_cart', function (ev) {
            ev.preventDefault();
            var $button = $(this);
            if ($button.data('update_change')) {
                return;
            }
            $button.data('update_change', true);

            var $pack = $(ev.target).closest('.js_pack');
            var pack_id = parseInt($pack.attr('data-pack-id'));

            var $products = $pack.find('input.pack-product-id');
            var product_ids = [];
            var datas = [];


            // Añadir todos los componentes del pack.
            $products.each(function (index) {
                var product_id, line_id, qty;
                line_id = parseInt($(this).attr('data-line-id'));
                qty = parseInt($(this).attr('data-qty'));
                product_id = parseInt($(this).attr('data-product-id'));

                var d = [line_id, product_id, qty];
                datas.push(d);
                product_ids.push(+product_id);
            });

            openerp.jsonRpc("/shop/cart/pack_update_json", 'call', {'pack_id': pack_id, 'datas': datas, 'product_ids':product_ids})
            .then(function (data) {
                $button.data('update_change', false);
                location.assign("/shop/cart");
            });

        });
    });


    // Actualizar las dependencias del producto principal.
    $('.oe_website_sale').on('change', 'input.js_variant_change, select.js_variant_change, ul[data-attribute_value_ids]', function (ev) {
        $('#product_packs').find('.js_pack').each(function () {
            var $pack = $(this);
            update_pack_price($pack);
        });
    });
});
