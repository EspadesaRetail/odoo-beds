# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Mail Validator',
    'version': '1.0',
    'category': 'Partner',
    'description': """
Function to validate mails from a list
==============================================
   Search sampling field in a list of mails
==============================================

    """,
    'summary': 'Mail Validator from partners',
    'depends': ['base'],
    'data': [
        'security/mail_validator_security.xml',
        'security/ir.model.access.csv',
        'views/mail_validator_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 118,
}
