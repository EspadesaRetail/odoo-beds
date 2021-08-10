# -*- coding: utf-8 -*-
import openerp
from openerp import tools, api
from openerp.osv import osv, fields

import logging
_logger = logging.getLogger(__name__)


class product_offer(osv.osv):
    _inherit = "product.offer"

    # Devuelve el producto de regalo si está definido en una oferta.
    def get_present_by_product(self, product_id):
        cr, uid, context = self.env.cr, self.env.uid, {}
        present_id = None

        if self.offer_type == 'present':
            present_id = self.present_id

            if self.present_ids:
                pop_obj = self.pool.get('product.offer.present')

                # Oferas basadas en un producto individual.
                ids = pop_obj.search(cr, uid, [('offer_id', '=', self.id),('product_id', '=', product_id.id)],context=context)
                if ids:
                    present_id = pop_obj.browse(cr, uid, ids[0]).present_id
        return present_id
