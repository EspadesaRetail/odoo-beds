# -*- coding: utf-8 -*-
from openerp import api, tools
from openerp.osv import osv, fields, expression
from openerp.addons.cs_model.models.product import product_template

import logging
_logger = logging.getLogger(__name__)


class mass_mailing_contact(osv.Model):
    _inherit = 'mail.mass_mailing.contact'

    _columns = {
        'phone': fields.char("Teléfono"),
    }
