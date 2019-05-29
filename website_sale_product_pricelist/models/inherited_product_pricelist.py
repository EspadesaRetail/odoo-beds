# Copyright 2019 Alberto Calvo Bazco
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class InheritedProductPricelist(models.Model):

    _inherit = 'product.pricelist'

    product_pricelist_ids = fields.One2many(
        string='Products Pricelists',
        comodel_name='website.sale.product.pricelist',
        inverse_name='pricelist_id')

    default_pricelist = fields.Boolean(
        string='Default Pricelist',
        default=False)
