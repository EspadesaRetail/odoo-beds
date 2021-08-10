# -*- coding: utf-8 -*-
from openerp import api, tools
from openerp.osv import osv, fields, expression
from openerp.addons.cs_model.models.product import product_template

import logging
_logger = logging.getLogger(__name__)


class beds_crm_claim(osv.osv):
    _inherit = ['crm.claim']

    _columns = {
        'external_ref': fields.char('Referencia pedido'),
        'city': fields.char('Población'),
        'zip': fields.char('Código postal'),
        'shop': fields.char("Tienda bed's"),

        'solucion': fields.char("Solución esperada"),
        

    }
