# -*- coding: utf-8 -*-
from openerp import http
from datetime import datetime
from openerp import tools
from openerp.http import request
from openerp.addons.cs_theme.controllers.main import cs_website_sale

import logging
_logger = logging.getLogger(__name__)


class offer_website_sale(cs_website_sale):
    @http.route(['/ofertas'], type='http', auth="public", website=True)
    def ofertas(self, search=None, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        """
        Leer todos los productos con oferta activa.
        Excepción: Super ofertas.
        """
        product_ids = []
        Offer = pool.get('product.offer')
        offer = False
        dt = datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        offer_ids = Offer.search(cr, uid, [('datetime_start', '<=', dt),
            ('datetime_end', '>=', dt), ('code', '!=', 'SO')],
            context=context)

        if offer_ids:
            offer_ids = Offer.browse(cr, uid, offer_ids, context=context)
            offer = offer_ids[0]
            for o in offer_ids:
                if o.product_offer_group_id:
                    product_ids += o.product_offer_group_id._get_products_of_group()

        product_ids = [p.id for p in product_ids]
        values = super(offer_website_sale, self).shop_products(product_ids=product_ids)

        product_ids = values['products']

        Categ = pool['product.public.category']
        Data = pool['ir.model.data']

        categ_ids = [
            Data.xmlid_to_res_id(cr, uid, 'beds_model.categ_colchones'),
            Data.xmlid_to_res_id(cr, uid, 'beds_model.categ_bases'),
            Data.xmlid_to_res_id(cr, uid, 'beds_model.categ_almohadas'),
            Data.xmlid_to_res_id(cr, uid, 'beds_model.categ_textil'),
        ]

        categ_ids = Categ.browse(cr, uid, categ_ids, context=context)

        bins = {}
        for c in categ_ids:
            bins[c.id] = {'category': c, 'products': []}

        bins['OTHERS'] = {'category': False, 'products': []}

        # Seleccionar los productos para cada una de las categorías que hay en el menu
        for p in product_ids:
            if p.public_categ_ids:
                categ = p.public_categ_ids[0]
                if categ.parent_id:
                    categ = categ.parent_id

                if categ.id in bins.keys():
                    bins[categ.id]['products'].append(p)
                else:
                    bins['OTHERS']['products'].append(p)

        # Quitar la categorias que no tienen productos.
        categ_ids = [c for c in categ_ids if bins[c.id]['products']]

        values['bins'] = bins
        values['categories'] = categ_ids

        values['offer'] = offer

        return request.website.render("cs_offer.offers", values)

    @http.route(['/black-friday'], type='http', auth="public", website=True)
    def black_friday(self, search=None, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        """
        Leer todos los productos que forman parte de la campaña Black Friday.
        Código de oferta : BF
        """
        product_ids = []
        Offer = pool.get('product.offer')
        offer_ids = Offer.search(cr, uid, [('code','=','BF')], context=context)
        if offer_ids:
            offer_ids = Offer.browse(cr, uid, offer_ids, context=context)
            for o in offer_ids:
                if o.product_offer_group_id:
                    product_ids += o.product_offer_group_id._get_products_of_group()
        else:
            """
            Si no hay códigos de oferta BF (Black Friday) redirigimos a Ofertas
            """
            return request.redirect("/ofertas", code=301)

        product_ids = [p.id for p in product_ids]
        values = super(offer_website_sale, self).shop_products(product_ids=product_ids)

        product_ids = values['products']


        Categ = pool['product.public.category']
        Data = pool['ir.model.data']

        categ_ids = [
            Data.xmlid_to_res_id(cr, uid, 'beds_model.categ_colchones'),
            Data.xmlid_to_res_id(cr, uid, 'beds_model.categ_bases'),
            Data.xmlid_to_res_id(cr, uid, 'beds_model.categ_almohadas'),
            Data.xmlid_to_res_id(cr, uid, 'beds_model.categ_textil'),
        ]
        categ_ids = Categ.browse(cr, uid, categ_ids, context=context)

        bins = {}
        for c in categ_ids:
            bins[c.id] = {'category': c, 'products': []}

        bins['OTHERS'] = {'category': False, 'products': []}


        # Seleccionar los productos para cada una de las categorías que hay en el menu
        for p in product_ids:
            if p.public_categ_ids:
                categ = p.public_categ_ids[0]
                if categ.parent_id:
                    categ = categ.parent_id

                if categ.id in bins.keys():
                    bins[categ.id]['products'].append(p)
                else:
                    bins['OTHERS']['products'].append(p)

        values['bins'] = bins
        values['categories'] = categ_ids

        return request.website.render("cs_offer.offer_black_friday", values)
