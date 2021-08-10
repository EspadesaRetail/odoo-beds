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


class sale_order(osv.osv):
    _inherit = 'sale.order'

    # Añadir los datos relativos al pack.
    def _pack_cart_update(self, cr, uid, ids, product=None, set_qty=0, pack_id=None, pack_sequence=None, context=None, **kwargs):
        Sol = self.pool.get('sale.order.line')
        Product = self.pool.get('product.product')

        for so in self.browse(cr, uid, ids, context=context):

            product_id = Product.browse(cr,uid,product)

            values = {
                'order_id': so.id,
                'name': product_id.name,
                'product_id': product_id.id,
                'product_uom_qty' : set_qty,
                'price_unit': product_id.price,
                'price_reduce': product_id.price,
                'lst_price': product_id.price,
                'pack_id' : pack_id.id,
                'pack_sequence' : pack_sequence,
            }

            if so.order_line:
                values['sequence'] = so.order_line[-1].sequence + 1

            line_id = Sol.create(cr, uid, values, context = context)

        return {'line_id': line_id, 'quantity': set_qty}




# Calcular el precio neto de una línea de producto, en base al proeducto.
class SaleOrderLine(osv.Model):
    _inherit = "sale.order.line"

    # Borrar las líneas del pack
    def unlink(self, cr, uid, ids, context=None):
        for sol in self.browse(cr, uid, ids, context=context):
            if sol.pack_id:
                ids = self.search(cr, uid, [('order_id', '=', sol.order_id.id),('pack_id','=', sol.pack_id.id),('pack_sequence','=', sol.pack_sequence)])

        return super(SaleOrderLine, self).unlink(cr, uid, ids, context=context)
