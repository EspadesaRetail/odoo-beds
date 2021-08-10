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

    # Update promotion lines at create
    def create(self, cr, uid, vals, context=None):
        if not context:
            context = {}
        chk_recursion = context.get('chk_recursion', False)
        new_id = super(sale_order_line, self).create(cr, uid, vals, context=context)
        if not chk_recursion:
            for sol in self.browse(cr, uid, [new_id], context=context):
                sol._siniva_update_order_with_promo()

        return new_id

    # Update promotion lines at write
    def write(self, cr, uid, ids, vals, context=None):
        if not context:
            context = {}
        chk_recursion = context.get('chk_recursion', False)
        res = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        if not chk_recursion:
            for sol in self.browse(cr, uid, ids, context=context):
                sol._siniva_update_order_with_promo()
        return res

    def _siniva_update_order_with_promo(self):
        cr, uid, context = self.env.cr, self.env.uid, {'chk_promo' : True}
        line_obj = self.pool.get('sale.order.line')
        line_id = self

        for offer_id in line_id.product_id.active_product_offer_ids:
            # Campaña sin iva.
            if offer_id.offer_type == 'siniva':
                line_id.with_context(chk_recursion = True ).write({ 'lst_price': self.product_id.lst_price * (1 - offer_id.siniva_dto / 100)})
