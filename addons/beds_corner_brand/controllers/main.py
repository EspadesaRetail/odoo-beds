# -*- coding: utf-8 -*-
import sys
import base64
import werkzeug
import werkzeug.urls
import locale
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slugify

##from openerp.addons.web.controllers.main import login_redirect
from openerp.tools import html_escape as escape
from openerp.addons.website_sale.controllers.main import *
from openerp.osv import osv

import math
import json
import logging
_logger = logging.getLogger(__name__)


class beds_website_corner_brand(http.Controller):

    # Calcular los enlaces internos a las fichas de productos.
    def enlaces(self, corner_brand):

        enlaces = []
        for brand in corner_brand:
            enlaces = enlaces.append(brand.corner_brand_products_ids.name)
        return enlaces

    @http.route([
        '/Pikolin',
        '/pikolin',
        '/<model("corner.brand"):brand>',
    ], type='http', auth="public", website=True)
    def corner_brand(self, brand=None, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        # Si ha llegado un name, comprobamos que existe para poder mostrar
        # la página correcta con sus fichas correspondientes
        Brand = request.registry['corner.brand']
        if brand:
            brand = Brand.search(cr, SUPERUSER_ID, [('id','=', int(brand))], context=context, limit=1)
            brand = Brand.browse(cr, SUPERUSER_ID, brand[0], context=context)
            if not brand:
                return request.redirect('/', code=301)
        else: # Siempre que se acceda como marca Pikolin
            brand = Brand.search(cr, SUPERUSER_ID, [('name','=', 'Pikolin')], context=context, limit=1)
            brand = Brand.browse(cr, SUPERUSER_ID, brand[0], context=context)
            if not brand:
                return request.redirect('/', code=301)

        keep = QueryURL('/')

        request.context.update({'show_corner_brand': True})

        values = {
            'keep' : keep,
            'image' : brand.image,
            'brand' : brand,
            'name' : brand.name,
            'title' : brand.title,
            'subtitle' : brand.subtitle,
            'product_cards' : brand.corner_brand_products_ids,
        }

        return request.website.render("beds_corner_brand.brand", values)
