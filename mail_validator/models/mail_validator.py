
from odoo import models, fields, api, _


# ----------------------------------------------------------
# mail validator tables
# ----------------------------------------------------------

class PartnerMailList(models.Model):
    _name = 'partner.mail.list'

    enterprise = fields.Integer(
        string=_('Enterprise Number'),
        required=True)
    shop = fields.Integer(
        string=_('Shop'),
        required=True)
    name = fields.Char(
        string=_('Shop Name'))
    shop_format = fields.Char(
        string=_('Shop Format'))
    shop_zone = fields.Char(
        string=_('Shop Zone'))
    partner_number = fields.Integer(
        string=_('Partner Number'),
        required=True)
    email = fields.Char(
        string=_('Email'))
    type_mail = fields.Char(
        string=_('Type Mail'))
    reason_mail = fields.Char(
        string=_('Reason'))

    @api.model
    def create(self, vals):
        if vals.get('email') and '@' in vals.get('email'):
            PartnerMailPattern = self.env['partner.mail.pattern']
            valor_type = 0
            for pattern in PartnerMailPattern.search([('type', '=', 'C')]):
                if pattern.name.upper() in vals.get('email').upper():
                    vals['type_mail'] = 'CONTACTO'
                    vals['reason_mail'] = 'Email de contacto genérico'
                    valor_type = 1
                    return super(PartnerMailList, self).create(vals)
            for pattern in PartnerMailPattern.search([('type', '=', 'S')]):
                if pattern.name.upper() in vals.get('email').upper():
                    vals['type_mail'] = 'TIENDA'
                    vals['reason_mail'] = 'Dirección de email de tienda'
                    valor_type = 1
                    return super(PartnerMailList, self).create(vals)
            for pattern in PartnerMailPattern.search([('type', '=', 'P')]):
                if pattern.name.upper() in vals.get('email').upper():
                    vals['type_mail'] = 'INCORRECTO'
                    vals['reason_mail'] = 'Email no correcto'
                    valor_type = 1
                    return super(PartnerMailList, self).create(vals)
            if valor_type == 0:
                vals['type_mail'] = 'VALIDO'
                vals['reason_mail'] = 'Email aparentemente correcto'
        elif vals.get('email') and '@' not in vals.get('email'):
            vals['type_mail'] = 'ERROR'
            vals['reason_mail'] = 'No contiene símbolo de @'
        return super(PartnerMailList, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('email') and '@' in vals.get('email'):
            PartnerMailPattern = self.env['partner.mail.pattern']
            valor_type = 0
            for pattern in PartnerMailPattern.search([('type', '=', 'C')]):
                if pattern.name.upper() in vals.get('email').upper():
                    vals['type_mail'] = 'CONTACTO'
                    vals['reason_mail'] = 'Email de contacto genérico'
                    valor_type = 1
                    return super(PartnerMailList, self).write(vals)
            for pattern in PartnerMailPattern.search([('type', '=', 'S')]):
                if pattern.name.upper() in vals.get('email').upper():
                    vals['type_mail'] = 'TIENDA'
                    vals['reason_mail'] = 'Dirección de email de tienda'
                    valor_type = 1
                    return super(PartnerMailList, self).write(vals)
            for pattern in PartnerMailPattern.search([('type', '=', 'P')]):
                if pattern.name.upper() in vals.get('email').upper():
                    vals['type_mail'] = 'INCORRECTO'
                    vals['reason_mail'] = 'Email no correcto'
                    valor_type = 1
                    return super(PartnerMailList, self).write(vals)
            if valor_type == 0:
                vals['type_mail'] = 'VALIDO'
                vals['reason_mail'] = 'Email aparentemente correcto'
        elif vals.get('email') and '@' not in vals.get('email'):
            vals['type_mail'] = 'ERROR'
            vals['reason_mail'] = 'No contiene símbolo de @'
        return super(PartnerMailList, self).write(vals)


class PartnerMailPattern(models.Model):
    _name = 'partner.mail.pattern'

    name = fields.Char(
        string=_('Name'),
        required=True)
    type = fields.Selection(
        [('C', _('Contact Mail')),
         ('S', _('Shop Mail')),
         ('P', _('Pattern'))],
        string=_("Pattern Type"),
        default='P')
