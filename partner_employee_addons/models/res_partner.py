
from odoo import models, fields, api, _


# ----------------------------------------------------------
# change password wizard
# ----------------------------------------------------------

class UpdateResPartnerWizard(models.TransientModel):
    """ A wizard to manage the massive updates of partners. """
    _name = "update.res.partner.wizard"
    _description = "Update Partner Wizard"

    def _default_partner_ids(self):
        partner_ids = self._context.get('active_model') == 'res.partner' and self._context.get('active_ids') or []
        return [
            (0, 0, {'name': partner.name,
                    'partner_id': partner.id,
                    'parent_id': partner.parent_id,
                    'type': partner.type,
                    'user_id': partner.user_id})
            for partner in self.env['res.partner'].browse(partner_ids)
        ]

    partner_ids = fields.One2many('update.res.partner', 'wizard_id', string='Partners', default=_default_partner_ids)

    @api.multi
    def update_button(self):
        self.ensure_one()
        self.partner_ids.update_button()
        return {'type': 'ir.actions.act_window_close'}


class UpdateResPartner(models.TransientModel):
    """ A model to configure partners in the massive update wizard. """
    _name = 'update.res.partner'
    _description = 'Massive Update, Partner Wizard'

    wizard_id = fields.Many2one('update.res.partner.wizard', string='Wizard', required=True, ondelete='cascade')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True, ondelete='cascade')
    name = fields.Char(string='Name')
    parent_id = fields.Many2one('res.partner', string='Related Company')
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Shipping address'),
         ('other', 'Other address'),
         ("private", "Private Address"),
        ], string='Address Type',
        default='contact',
        help="Used by Sales and Purchase Apps to select the relevant address depending on the context.")
    category_id = fields.Many2many('res.partner.category', column1='partner_id',
                                    column2='category_id', string='Tags')
    user_id = fields.Many2one('res.users', string='Salesperson',
        help='The internal user in charge of this contact.')

    @api.multi
    def update_button(self):
        for line in self:
            line.partner_id.write({'name': line.name,
                                   'parent_id': line.parent_id.id,
                                   'type': line.type,
                                   'user_id': line.user_id.id})
        self.write({'name': False,
                    'parent_id': False,
                    'type': False,
                    'user_id': False})
