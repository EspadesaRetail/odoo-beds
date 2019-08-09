
from odoo import models, fields, api, _


class ResUsersTeam(models.Model):
    _name = 'res.users.team'

    name = fields.Char(
        string=_('Team Name'),
        required=True,
        translate=True)
    team = fields.Char(
        string=_('Team Sequence'),
        default=_('New'))
    description = fields.Text(
        string='Description',
        translate=True)
    user_ids = fields.One2many(
        comodel_name='res.users',
        inverse_name='team_id',
        string='Users')

    @api.model
    def create(self, vals):
        if vals.get('team', _('New')) == _('New'):
            vals['team'] = self.env['ir.sequence'].next_by_code(
                'res.users.team') or '/'
        return super(ResUsersTeam, self).create(vals)


class ResUsersShopRole(models.Model):
    _name = 'res.users.shop_role'

    name = fields.Char(
        string='Name',
        required=True)
    description = fields.Text(
        string='Description')
    user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Users')


class ResUsers(models.Model):
    _inherit = 'res.users'

    team_id = fields.Selection(
        selection='_list_all_teams',
        string='User Team')
    shop_role_ids = fields.Many2many(
        comodel_name='res.users.shop_role',
        string='Shop Role')
    role_name = fields.Char(
        string='Role Name',
        related='shop_role_ids.name',
        store=True)

    @api.model
    def _list_all_teams(self):
        self._cr.execute("SELECT team, name FROM res_users_team ORDER BY team")
        return self._cr.fetchall()
