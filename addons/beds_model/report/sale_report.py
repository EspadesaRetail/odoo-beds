 # -*- coding: utf-8 -*-
from openerp.osv import fields, osv
from openerp import tools

class sale_report(osv.osv):
    _inherit = "sale.report"
    _columns = {


        # Añadir la base imponible de la línea del pedido.
        'tax_base': fields.float('Base Imponible', readonly=True),
    }

    def _select(self):
        s = super(sale_report, self)._select()

        s += ", l.tax_base"

        return s

    def _group_by(self):
        s = super(sale_report, self)._group_by()

        s += ", l.tax_base"

        return s
