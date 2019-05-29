# Copyright 2019 Alberto Calvo Bazco
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _


class InheritedProductTemplate(models.Model):

    _inherit = 'product.template'

    principal_variant_id = fields.Many2one(
        string='Principal Variant',
        comodel_name='product.product')
    principal_attribute_id = fields.Many2one(
        string='Principal Attribute',
        comodel_name='product.attribute')
    product_pricelist_ids = fields.One2many(
        string='Prices',
        comodel_name='website.sale.product.pricelist',
        inverse_name='product_template_id')
    product_variant_id = fields.Many2one(
        compute='_compute_product_variant_id')
    visible_variant = fields.Boolean(
        compute='_compute_visible_variant',
        default=False)

    @api.onchange('principal_variant_id')
    def _onchange_principal_variant_id(self):
        if self.principal_variant_id:
            self.product_variant_id = self.principal_variant_id

    @api.depends('product_variant_count')
    def _compute_visible_variant(self):
        if self.product_variant_count > 1:
            self.visible_variant = True

    @api.depends('principal_variant_id')
    def _compute_product_variant_id(self):
        if not self.principal_variant_id:
            for p in self:
                p.product_variant_id = p.product_variant_ids[:1].id
        else:
            self.product_variant_id = self.principal_variant_id
