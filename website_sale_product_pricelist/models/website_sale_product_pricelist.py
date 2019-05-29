# Copyright 2019 Alberto Calvo Bazco
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _


class WebsiteSaleProductPricelist(models.Model):

    _name = 'website.sale.product.pricelist'
    _description = 'Website Pricelist to online sales'

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id

    display_name = fields.Char(
        compute='_compute_display_name', store=True, index=True)
    taxes_id = fields.Many2many(
        'account.tax',
        'website_product_taxes_rel',
        'prod_id',
        'tax_id',
        help="Taxes used when selling the product.",
        string='Tax',
        domain=[('type_tax_use', '=', 'sale')])
    price = fields.Float(
        string='Price',
        digits=dp.get_precision('Product Price'),
        help="Price at which the product is sold to customers.")
    product_template_id = fields.Many2one(
        comodel_name='product.template',
        string='Product Template Related')
    product_product_id = fields.Many2one(
        comodel_name='product.product',
        string='Product Related')
    pricelist_id = fields.Many2one(
        comodel_name='product.pricelist',
        string='Assigned Pricelist')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=_default_company_id)

    @api.onchange('product_template_id')
    def _onchange_product_template_id(self):
        res = {'domain': {'product_product_id': []}}
        if self.product_template_id:
            res['domain']['product_product_id'] = [
                ('product_tmpl_id', '=', self.product_template_id.id)]
        return res

    @api.onchange('product_product_id')
    def _onchange_product_product_id(self):
        if self.product_product_id.product_tmpl_id != self.product_template_id:
            self.product_template_id = self.product_product_id.product_tmpl_id

    @api.constrains('product_template_id', 'product_product_id')
    def _check_products(self):
        if any(item.product_product_id.product_tmpl_id != item.product_template_id for item in self):
            raise ValidationError(
                _('The Product should be related with Template'))
        return True

    @api.depends('product_template_id', 'product_product_id', 'pricelist_id')
    def _compute_display_name(self):
        for p in self:
            if p.product_product_id and p.pricelist_id:
                p.display_name = '[' + p.product_product_id.display_name + \
                    '] [' + p.pricelist_id.name + ']'

    # A la hora de crear el registro en website.sale.product.pricelist, vemos,
    # si su tarifa asignadas es la marcada por defecto y su product.product, es
    # a su vez el marcado como variante principal, guardamos el precio que se
    # designa también en la tabla product.template
    @api.model
    def create(self, vals):
        vals = self._check_default_pricelist(vals)
        vals = self._check_principal_variant(vals)
        if vals.get('default_pricelist') and vals.get('principal_variant'):
            prod_template = self.env['product.template'].browse(
                vals['product_template_id'])
            prod_template = prod_template.write({
                'list_price': vals['price'],
                'taxes_id': vals['taxes_id']
            })
            print(prod_template)
        return super(WebsiteSaleProductPricelist, self).create(vals)

    @api.multi
    def write(self, vals):
        values = vals
        values = self._check_update_values(values)
        values = self._check_default_pricelist(values)
        values = self._check_principal_variant(values)
        values = self._update_product_template(values)
        values = self._update_product_attributes(values)
        return super(WebsiteSaleProductPricelist, self).write(vals)

    def _update_product_template(self, vals):
        if vals.get('default_pricelist') and vals.get('principal_variant'):
            prod_template = self.env['product.template'].browse(
                vals['product_template_id'])
            if not vals.get('taxes_id'):
                prod_template = prod_template.write({
                    'list_price': vals['price']
                })
            elif not vals.get('price'):
                prod_template = prod_template.write({
                    'taxes_id': vals['taxes_id']
                })
            else:
                prod_template = prod_template.write({
                    'list_price': vals['price'],
                    'taxes_id': vals['taxes_id']
                })
        return vals

    @api.multi
    def _update_product_attributes(self, vals):
        print(vals)
        print(vals['product_product_id'])
        if not vals.get('principal_variant') and vals.get('price'):
            prod_prod = self.env['product.product'].browse(
                vals['product_product_id'])
            print("PRODUCTO:")
            print("=========")
            print(prod_prod.id)
            print("PRECIOS: ")
            print("=========")
            print(vals['price'])
            price_modificator = vals['price'] - prod_prod.list_price
            print(price_modificator)
            print("EXTRA PRICE:")
            print("============")
            print(prod_prod.price_extra)
            print("EXTRA VALUES:")
            print("=============")
            print(prod_prod.product_tmpl_id)
            print(prod_prod.attribute_value_ids)
            prod_prod = prod_prod.write({
                'price_extra': price_modificator
            })
            attr_value_model = self.env['product.template.attribute.value']
            attr_value_found = attr_value_model.search([
                ('product_tmpl_id', 'in', prod_prod.product_tmpl_id),
                ('product_attribute_value_id', 'in', prod_prod.attribute_value_ids),
            ], limit=1)

            '''values = self.env['product.template.attribute.value'].search([
                ('product_tmpl_id', 'in', prod_prod.product_tmpl_id),
                ('product_attribute_value_id', 'in', prod_prod.attribute_value_ids),
            ])'''
            print(attr_value_found)
        return vals

    def _check_update_values(self, vals):
        vals = dict(vals or {})
        if not vals.get('pricelist_id'):
            vals.update(pricelist_id=self.pricelist_id.id)
        if not vals.get('product_template_id'):
            vals.update(product_template_id=self.product_template_id.id)
        if not vals.get('product_product_id'):
            vals.update(product_product_id=self.product_product_id.id)
        return vals

    def _check_default_pricelist(self, vals):
        vals = dict(vals or {})
        if vals.get('pricelist_id') and vals.get('product_product_id'):
            pricelist = self.env['product.pricelist'].browse(
                vals['pricelist_id'])
            if pricelist.default_pricelist:
                vals.update(default_pricelist=True)
        return vals

    def _check_principal_variant(self, vals):
        vals = dict(vals or {})
        if vals.get('product_template_id') and vals.get('product_product_id'):
            ppal_v = self.env['product.template'].browse(
                vals['product_template_id'])
            if ppal_v.principal_variant_id and ppal_v.principal_variant_id.id == vals.get('product_product_id'):
                vals.update(principal_variant=True)
        return vals
