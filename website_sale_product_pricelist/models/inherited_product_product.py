# Copyright 2019 Alberto Calvo Bazco
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from odoo import fields, models

import logging
import re

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

from odoo.addons import decimal_precision as dp

from odoo.tools import float_compare, pycompat


class InheritedProductProduct(models.Model):

    _inherit = 'product.product'

    product_pricelist_ids = fields.One2many(
        string='Prices',
        comodel_name='website.sale.product.pricelist',
        inverse_name='product_product_id')

    @api.multi
    def price_compute(self, price_type, uom=False, currency=False, company=False):
        # TDE FIXME: delegate to template or not ? fields are reencoded here ...
        # compatibility about context keys used a bit everywhere in the code
        if not uom and self._context.get('uom'):
            uom = self.env['uom.uom'].browse(self._context['uom'])
        if not currency and self._context.get('currency'):
            currency = self.env['res.currency'].browse(
                self._context['currency'])

        products = self
        if price_type == 'standard_price':
            print("STANDAR PRICE")
            # standard_price field can only be seen by users in base.group_user
            # Thus, in order to compute the sale price from the cost for users not in this group
            # We fetch the standard price as the superuser
            products = self.with_context(force_company=company and company.id or self._context.get(
                'force_company', self.env.user.company_id.id)).sudo()

        prices = dict.fromkeys(self.ids, 0.0)
        for product in products:
            prices[product.id] = product[price_type] or 0.0
            if price_type == 'list_price':
                if product.product_pricelist_ids:
                    domain = [
                        ('pricelist_id', '=', self._context.get('pricelist')),
                        ('product_product_id', '=', product.id)]
                    order = 'create_date DESC'
                    for product_pricelist in self.env['website.sale.product.pricelist'].sudo().search(domain, order=order, limit=1):
                        prices[product.id] += product_pricelist.extra_price
                else:
                    prices[product.id] += product.price_extra
                # we need to add the price from the attributes that do not generate variants
                # (see field product.attribute create_variant)
                if self._context.get('no_variant_attributes_price_extra'):
                    # we have a list of price_extra that comes from the attribute values, we need to sum all that
                    prices[product.id] += sum(self._context.get(
                        'no_variant_attributes_price_extra'))

            if uom:
                if product.product_pricelist_ids:
                    domain = [
                        ('pricelist_id', '=', self._context.get('pricelist')),
                        ('product_product_id', '=', product.id)]
                    order = 'create_date DESC'
                    for product_pricelist in self.env['website.sale.product.pricelist'].sudo().search(domain, order=order, limit=1):
                        prices[product.id] = product_pricelist.computed_price_discount
                else:
                    prices[product.id] = product.uom_id._compute_price(
                        prices[product.id], uom)

            # Convert from current user company currency to asked one
            # This is right cause a field cannot be in more than one currency
            if currency:
                prices[product.id] = product.currency_id._convert(
                    prices[product.id], currency, product.company_id, fields.Date.today())

        return prices
