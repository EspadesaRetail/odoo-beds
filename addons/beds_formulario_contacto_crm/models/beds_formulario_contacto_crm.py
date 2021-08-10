# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class beds_formulario_contacto_crm(models.Model):
    _name = 'beds.formulario.contacto.crm'
    _description = 'Session info for SLABS Rest API'

    name = fields.Char(string='Enviroment',
                       translate=True)
    url_environment = fields.Char(string='URL')
    api_version_form = fields.Char(string='Version (form)',
                                   translate=True)
    api_version_credentials = fields.Char(string='Version (credentials)',
                                          translate=True)
    description = fields.Char(string='Description',
                              translate=True)
    client_id = fields.Char(string='Client ID',
                            translate=True)
    client_secret = fields.Char(string='Client Secret',
                                translate=True)
    username = fields.Char(string='User',
                           translate=True)
    password = fields.Char(string='Password',
                           translate=True)
    type = fields.Char(string='Type',
                       translate=True)
    accountId = fields.Char(string='Account ID',
                            translate=True)
    rgpd_policy_version = fields.Char(string='GDPR Privacy Policy Version',
                            translate=True)
    rgpd_policy_url = fields.Char(string='GDPR Privacy Policy URL',
                            translate=True)
    rgpd_terms_version = fields.Char(string='GDPR Privacy Terms Version',
                            translate=True)
    rgpd_terms_url = fields.Char(string='GDPR Privacy Terms URL',
                            translate=True)
