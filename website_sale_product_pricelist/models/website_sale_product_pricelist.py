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
    default_pricelist = fields.Boolean(
        string='Default Pricelist?',
        related='pricelist_id.default_pricelist',
        readonly=True,
        store=True)
    price_discount = fields.Char(
        string='Price',
        related='pricelist_id.item_ids.price',
        context="[('product_id', '=', product_product_id)]")
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        default=_default_company_id)
    product_template_attribute_value_id = fields.Many2one(
        comodel_name='product.template.attribute.value',
        string='Product Attribute Value',
        compute='_compute_product_template_attribute_value_id')
    price_extra = fields.Float(
        string='Extra Price',
        related='product_template_attribute_value_id.price_extra',
        readonly=True)
    list_price = fields.Float(
        string='Principal Variant Price',
        related='product_template_id.list_price',
        readonly=True)
    computed_amount_tax = fields.Float(
        string='Amount Tax',
        compute='_compute_amount_tax')

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

    @api.depends('product_product_id')
    def _compute_product_template_attribute_value_id(self):
        product = self.product_product_id
        attributes = self.product_template_id.principal_attribute_id.value_ids
        for attribute_id in attributes:
            for p in product.attribute_value_ids:
                if not (p.id != attribute_id.id):
                    value_id = p
                    domain = [('attribute_id', '=', product.principal_attribute_id.id),
                              ('product_tmpl_id', '=', product.product_tmpl_id.id),
                              ('product_attribute_value_id', '=', value_id.id)]
                    vals = self.env['product.template.attribute.value'].search(
                        domain)
                    self.product_template_attribute_value_id = vals

    @api.depends('price', 'taxes_id')
    def _compute_amount_tax(self):
        self.computed_amount_tax = self.price + (self.price * (self.taxes_id.amount / 100))

    ''' Al crear/modificar registros en website.sale.product.pricelist si su
        tarifa asignada es la marcada por defecto y su product.product, es a su
        vez el marcado como variante principal, guardamos el precio asignado
        también en la tabla product.template, mientras que si no es la variante
        por defecto, actualizamos además, el campo price_extra de la tabla que
        guarda los valores para cada atributo simpre dicho atributo sea el que
        se ha marcado como principal '''
    @api.model
    def create(self, vals):
        vals = self._check_product_template_attribute_values(vals)
        vals = self._check_default_pricelist(vals)
        vals = self._check_principal_variant(vals)
        vals = self._update_product_template(vals)
        vals = self._update_product_attribute(vals)
        return super(WebsiteSaleProductPricelist, self).create(vals)

    @api.multi
    def write(self, vals):
        values = vals
        values = self._check_update_values(values)
        values = self._check_default_pricelist(values)
        values = self._check_principal_variant(values)
        values = self._update_product_template(values)
        values = self._update_product_attributes(values)
        values = self._check_update_all_products(values)
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
        if vals.get('product_template_attribute_value_id') and vals.get('price') and vals.get('default_pricelist') and not vals.get('principal_variant'):
            attr_value = self.env['product.template.attribute.value'].browse(
                vals['product_template_attribute_value_id'])
            price_extra = round(vals.get('price') - vals.get('list_price'), 2)
            attr_value = attr_value.write({
                'price_extra': price_extra
            })
        return vals

    @api.multi
    def _update_product_attribute(self, vals):
        if vals.get('product_template_attribute_value_id') and vals.get('price') and vals.get('default_pricelist') and not vals.get('principal_variant'):
            domain = [('id', '=', vals.get('product_template_attribute_value_id').id)]
            attr_value = self.env['product.template.attribute.value'].search(
                domain)
            update = self.env['product.template.attribute.value'].browse(
                attr_value.id)
            price_extra = round(vals.get('price') - vals.get('list_price'), 2)
            update = update.write({
                'price_extra': price_extra
            })
        return vals

    def _check_update_all_products(self, vals):
        if vals.get('default_pricelist') and vals.get('principal_variant'):
            domain = [('product_template_id', '=', vals.get('product_template_id')),
                      ('pricelist_id', '=', vals.get('pricelist_id'))]
            pricelist = self.env['website.sale.product.pricelist'].search(
                domain)
            for p in pricelist:
                if p.id != self.id:
                    update = self.env['website.sale.product.pricelist'].browse(p.id)
                    update = update.write({
                        'price': p.price
                    })
        return vals

    def _check_update_values(self, vals):
        vals = dict(vals or {})
        if not vals.get('pricelist_id'):
            vals.update(pricelist_id=self.pricelist_id.id)
        if not vals.get('product_template_id'):
            vals.update(product_template_id=self.product_template_id.id)
            vals.update(list_price=self.product_template_id.list_price)
        if not vals.get('product_product_id'):
            vals.update(product_product_id=self.product_product_id.id)
        if not vals.get('product_template_attribute_value_id'):
            vals.update(
                product_template_attribute_value_id=self.product_template_attribute_value_id.id)
        return vals

    def _check_default_pricelist(self, vals):
        vals = dict(vals or {})
        if vals.get('pricelist_id') and vals.get('product_product_id') and not vals.get('default_pricelist'):
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

    def _check_product_template_attribute_values(self, vals):
        vals = dict(vals or {})
        product = self.env['product.product'].browse(
            vals['product_product_id'])
        template = self.env['product.template'].browse(
            vals['product_template_id'])
        attributes = template.principal_attribute_id.value_ids
        for attribute_id in attributes:
            for p in product.attribute_value_ids:
                if not (p.id != attribute_id.id):
                    value_id = p
                    domain = [('attribute_id', '=', product.principal_attribute_id.id),
                              ('product_tmpl_id', '=', product.product_tmpl_id.id),
                              ('product_attribute_value_id', '=', value_id.id)]
                    value = self.env['product.template.attribute.value'].search(
                        domain)
                    vals.update(product_template_attribute_value_id=value)
                    vals.update(list_price=template.list_price)
        return vals
