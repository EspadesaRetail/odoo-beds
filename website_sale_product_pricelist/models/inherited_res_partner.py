# Copyright 2019 Alberto Calvo Bazco
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError, ValidationError
from odoo import fields, models, api


class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    # NOT A REAL PROPERTY !!!!
    property_product_pricelist = fields.Many2one(
        'product.pricelist', 'Pricelist', compute='_compute_product_pricelist',
        inverse="_inverse_product_pricelist", company_dependent=False,
        help="This pricelist will be used, instead of the default one, for sales to the current partner")

    @api.multi
    @api.depends('country_id', 'state_id')
    def _compute_product_pricelist(self):
        company = self.env.context.get('force_company', False)
        try:
            res = self.env['product.pricelist']._get_partner_pricelist_multi(self.ids, company_id=company, state_id=self.state_id)
        except ValueError:
            res = self.env['product.pricelist']._get_partner_pricelist_multi(self.ids, company_id=company)
        for p in self:
            p.property_product_pricelist = res.get(p.id)
