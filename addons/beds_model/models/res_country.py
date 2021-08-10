# -*- coding: utf-8 -*-


from openerp import api, tools
from openerp.osv import osv, fields, expression

import logging
import json
_logger = logging.getLogger(__name__)


class res_country(osv.osv):
    """ Inherits country and adds published information """
    _inherit = 'res.country'

    _columns = {


        # Añadir datos complementarios a las tiendas bed's
        'country_beds': fields.boolean("País Bed's", help="Check this box if this country have Bed's shops."),

    }

    _defaults = {
        'country_beds': True,
    }
