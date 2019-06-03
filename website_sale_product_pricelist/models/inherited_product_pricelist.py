# Copyright 2019 Alberto Calvo Bazco
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _


class InheritedProductPricelist(models.Model):

    _inherit = 'product.pricelist'

    product_pricelist_ids = fields.One2many(
        string='Products Pricelists',
        comodel_name='website.sale.product.pricelist',
        inverse_name='pricelist_id')

    default_pricelist = fields.Boolean(
        string='Default Pricelist',
        default=False)

    country_ids = fields.Many2many(
        'res.country',
        'website_product_country_ids_rel',
        'prod_id',
        'country_id',
        string='Countries')

    state_ids = fields.Many2many(
        'res.country.state',
        'website_product_country_state_ids_rel',
        'prod_id',
        'state_id',
        string='States')

    @api.onchange('state_ids')
    def onchange_states(self):
        self.country_ids = [(6, 0, self.country_ids.ids + self.state_ids.mapped('country_id.id'))]

    @api.onchange('country_ids')
    def onchange_countries(self):
        self.state_ids = [(6, 0, self.state_ids.filtered(lambda state: state.id in self.country_ids.mapped('state_ids').ids).ids)]

    def _get_partner_pricelist_multi(self, partner_ids, company_id=None, state_id=None):
        """ Retrieve the applicable pricelist for given partners in a given company.

            It will return the first found pricelist in this order:
            First, the pricelist of the specific property (res_id set), this one
                   is created when saving a pricelist on the partner form view.
            Else, it will return the pricelist of the partner country group
            Else, it will return the generic property (res_id not set), this one
                  is created on the company creation.
            Else, it will return the first available pricelist

            :param company_id: if passed, used for looking up properties,
                instead of current user's company
            :return: a dict {partner_id: pricelist}
        """
        # `partner_ids` might be ID from inactive uers. We should use active_test
        # as we will do a search() later (real case for website public user).
        Partner = self.env['res.partner'].with_context(active_test=False)

        Property = self.env['ir.property'].with_context(force_company=company_id or self.env.user.company_id.id)
        Pricelist = self.env['product.pricelist']
        pl_domain = self._get_partner_pricelist_multi_search_domain_hook()

        # if no specific property, try to find a fitting pricelist
        result = Property.get_multi('property_product_pricelist', Partner._name, partner_ids)

        remaining_partner_ids = [pid for pid, val in result.items() if not val or
                                 not val._get_partner_pricelist_multi_filter_hook()]
        if remaining_partner_ids:
            # get fallback pricelist when no pricelist for a given country
            pl_fallback = (
                Pricelist.search(pl_domain + [('country_group_ids', '=', False)], limit=1) or
                Property.get('property_product_pricelist', 'res.partner') or
                Pricelist.search(pl_domain, limit=1)
            )
            # group partners by country, and find a pricelist for each country
            domain = [('id', 'in', remaining_partner_ids)]
            groups = Partner.read_group(domain, ['country_id'], ['country_id'])
            for group in groups:
                country_id = group['country_id'] and group['country_id'][0]
                if state_id:
                    pl = Pricelist.search(pl_domain + [('country_group_ids.country_ids', '=', country_id), ('country_ids', '=', country_id), ('state_ids', '=', state_id.id)], limit=1)
                else:
                    pl = Pricelist.search(pl_domain + [('country_group_ids.country_ids', '=', country_id)], limit=1)
                pl = pl or pl_fallback
                for pid in Partner.search(group['__domain']).ids:
                    result[pid] = pl

        return result
