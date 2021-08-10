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
                sol._present_update_order_with_promo()

        return new_id

    # Update promotion lines at write
    def write(self, cr, uid, ids, vals, context=None):
        res = super(sale_order_line, self).write(cr, uid, ids, vals, context=context)
        for sol in self.browse(cr, uid, ids, context=context):
            sol.delete_lines_of_promo()
            sol._present_update_order_with_promo()
        return res

    def unlink(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """ Update promotion lines at unlink """
        for sol in self.browse(cr, uid, ids, context=context):
            sol.delete_lines_of_promo()

        return super(sale_order_line, self).unlink(cr, uid, ids, context=context)

    def _present_update_order_with_promo(self):
        cr, uid, context = self.env.cr, self.env.uid, {'chk_promo' : True}
        line_obj = self.pool.get('sale.order.line')
        line_id = self
        for offer_id in line_id.product_id.active_product_offer_ids:

            # Regalos
            if offer_id.offer_type == 'present':
                present_id = offer_id.get_present_by_product(line_id.product_id)
                if present_id:
                     self.add_product_to_cart(order_id = line_id.order_id, product_id=present_id, price = 0, qty=line_id.product_uom_qty, offer_id=offer_id, offer_line_id=line_id )
