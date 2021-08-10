    # -*- coding: utf-8 -*-
from openerp import api, tools
from openerp.osv import osv, fields, expression

import logging
_logger = logging.getLogger(__name__)


class ir_cron(osv.osv):
    _inherit = 'ir.cron'

    # Permite ejecutar un proceso manualmente.
    def method_direct_trigger(self, cr, uid, ids, context=None):
        if context is None:
            context={}
        cron_obj = self.browse(cr, uid, ids, context=context)
        for cron in cron_obj:
            self._callback(cr, cron_obj.user_id.id, cron_obj.model, cron_obj.function, cron_obj.args, cron_obj.id)
        return True
