# -*- coding: utf-8 -*-
from openerp import api, tools
from openerp.osv import osv, fields, expression
from openerp.addons.cs_model.models.product import product_template

import logging
_logger = logging.getLogger(__name__)

class cs_cross_selling_product_template(osv.osv):
    _inherit = "product.template"

    def _cross_selling_products(self, cr, uid, product_id, context=None):
        _logger.debug("CROSS SELLING HIJO:" + str(product_id))

        cross = super(cs_cross_selling_product_template,self)._cross_selling_products(cr, uid, product_id, context)
        cross += [x.id for x in product_id.alternative_product_ids]
        return cross
