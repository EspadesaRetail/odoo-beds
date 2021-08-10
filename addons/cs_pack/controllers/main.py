# -*- coding: utf-8 -*-
import json
import logging
from openerp import SUPERUSER_ID
from openerp import http
from openerp.addons.web.controllers.main import *
from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.website.controllers.main import *
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers.main import *
from openerp.http import request
from openerp.tools import html_escape as escape
from openerp.tools.translate import _
import werkzeug
import math
from datetime import datetime

_logger = logging.getLogger(__name__)

from openerp.addons.cs_model.models.product import *
from openerp.addons.website_sale.models.product import product_public_category
import re
from time import sleep


class pack_website_sale(website_sale):
    """
    Permite actualizar el carrito con todos los productos de un pack.
    """
    @http.route(['/shop/cart/pack_update_json'], type='json', auth="public", methods=['POST'], website=True)
    def pack_cart_update_json(self, pack_id, datas, product_ids):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        pack_obj = pool['product.pack']
        pack_id = pack_obj.browse(cr, uid, pack_id, context=context)

        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        pricelist_id = request.session.get("pricelist")
        pack_list = [x.pack_sequence for x in order.order_line] or [0]
        pack_sequence = max(pack_list) + 10  # Permite borrar todas las lines del pack.

        for d in datas:
            order._pack_cart_update(product=int(d[1]), set_qty=int(d[2]), pack_id = pack_id, pack_sequence=pack_sequence)

        return True


    """
    Página de packs. Crea un página especifica con todos los packs existentes
    """
    @http.route(['/packs-descanso'], type='http', auth="public", website=True)
    def packs_descanso(self, search=None, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        # Leer la configuración del pack
        Config = pool.get('product.pack.config')
        dt = datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        config = Config.search(cr, uid, [('datetime_start', '<=', dt),
            ('datetime_end', '>=', dt)], limit=1,context=context)

        if config:
            config = Config.browse(cr, uid, config[0], context=context)

        # Leer todos los packs publicados
        Pack = pool.get('product.pack')
        pack = False
        pack_ids = Pack.search(cr, uid, [], context=context)
        if pack_ids:
            pack_ids = Pack.browse(cr, uid, pack_ids, context=context)
            pack_ids = [x for x in pack_ids if x.active_now]

        keep = QueryURL('/packs-descanso')

        values = {}
        values['config'] = config
        values['packs'] = pack_ids
        values['keep'] = keep
        values['get_pack_attribute_value_ids'] = self.get_pack_attribute_value_ids

        return request.website.render("cs_pack.packs_descanso", values)
