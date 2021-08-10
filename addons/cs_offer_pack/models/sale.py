# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow
import logging
_logger = logging.getLogger(__name__)


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    # Update promotion lines on create
    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        Offer = self.pool.get('product.offer')
        Pack = self.pool.get('product.pack')
        Line = self.pool.get('sale.order.line')

        pack_id = vals.get("pack_id", False)
        if pack_id:
            pack_id = Pack.browse(cr,uid,pack_id)

        # Detectar si es una línea de pack
        if pack_id and pack_id.active_now:
            offer_id = Offer.search(cr,uid,[('pack_ids','in', pack_id.id)], limit=1)
            if offer_id:
                offer_id = Offer.browse(cr,uid,offer_id)
                if offer_id.active_now:
                    vals["offer_id"] = offer_id.id
                    vals["pack_id"] = pack_id.id

        new_id = super(sale_order_line, self).create(cr, uid, vals, context=context)

        line_id = Line.browse(cr,uid,new_id)
        if line_id.offer_id and line_id.pack_id:
            line_id._pack_update_order_with_promo()

        return new_id


    # Update promotion lines on write
    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}

        res = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)

        chk_recursion = context.get('chk_recursion', False)
        if not chk_recursion:
            for sol in self.browse(cr, uid, ids, context=context):
                if sol.offer_id and sol.pack_id:
                    sol._pack_update_order_with_promo()

        return res

    @api.one
    def _pack_update_order_with_promo(self):

        # Pack + colchón + resto de pack de regalo
        if self.offer_id.offer_type == 'pack':
            category = self.product_id.product_tmpl_id.public_categ_ids

            # El colchón se cobra, el resto no.
            if category:
                category = category[0]
            if category and category.parent_id:
                category = category.parent_id
            if category and category.name != "COLCHONES":
                self.with_context(chk_recursion = True ).write({'price_unit':0, 'lst_price': 0 })

        # Pack + dto. adicional.
        elif  self.offer_id.offer_type == 'pack-dto':
            lst_price = self.product_id.lst_price * (1 - self.offer_id.additional_dto / 100)
            price = self.product_id.price * (1 - self.offer_id.additional_dto / 100)
            self.with_context(chk_recursion = True ).write({'price_unit': price, 'lst_price': price})
