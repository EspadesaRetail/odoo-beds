
from odoo import models, fields, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    team_id = fields.Many2one(
        comodel_name='res.users.team',
        string='User Team')
    shop_role_ids = fields.Many2many(
        comodel_name='res.users.shop_role',
        string='Shop Role')


class ResUsersTeam(models.Model):
    _name = 'res.users.team'

    name = fields.Selection(
        [('Administrators', 'Administrators'),
         ('Managers', 'Managers'),
         ('Commercial', 'Commercial Managers'),
         ('Franchisees', 'Franchisees'),
         ('Shop', 'Shop')],
        'Team Name',
        required=True,
        help=" * The 'Administrators' option is used to enable special access, only for Administrator Users.\n"
             " * The 'Managers' option is used to enable view access at selected users below its range.\n"
             " * The 'Commercial Managers' option is used to enable view access at shop users below its range.\n"
             " * The 'Franchisees' option is used to design user as the name says.\n"
             " * The 'Shop' option is used to design user as Shop.")
    description = fields.Text(
        string='Description')
    user_ids = fields.One2many(
        comodel_name='res.users',
        inverse_name='team_id',
        string='Users')


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
