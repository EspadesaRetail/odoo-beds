# -*- coding: utf-8 -*-


from openerp import api, tools
from openerp.osv import osv, fields, expression

import logging
import json
_logger = logging.getLogger(__name__)


class res_country_state(osv.osv):
    """ Inherits country state and adds published information """
    _inherit = 'res.country.state'

    _columns = {


        # Añadir datos complementarios a las tiendas bed's
        'country_state_beds': fields.boolean("Provincia Bed's", help="Check this box if this country state have Bed's shops."),

    }

    _defaults = {
        'country_state_beds': False,
    }
