# -*- coding: utf-8 -*-
from openerp import api, tools
from openerp.osv import osv, fields, expression

import logging
_logger = logging.getLogger(__name__)


class attachment(osv.osv):
    _inherit = 'ir.attachment'
    _order = 'sequence, id desc'

    _columns = {
        'sequence': fields.integer('Sequence', help="Indica el orden en el que se muestran los adjuntos."),
    }

    _defaults = {
        'sequence': 0,
    }
