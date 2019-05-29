# Copyright 2019 Alberto Calvo Bazco
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class InheritedProductProduct(models.Model):

    _inherit = 'product.product'

    product_pricelist_ids = fields.One2many(
        string='Prices',
        comodel_name='website.sale.product.pricelist',
        inverse_name='product_product_id')
