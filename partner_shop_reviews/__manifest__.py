# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Shop Reviews',
    'version': '3.0',
    'author': 'Alberto Calvo',
    'category': 'Partner',
    'description': """
Adds to Partner base model
==============================================
Get data about reviews from Google My Business
==============================================

Addon to add reviews into partner like shop.
    """,
    'summary': 'Get data about reviews from Google My Business',
    'depends': ['base'],
    'data': [
        'data/ir_sequence_data.xml',
        'security/partner_security.xml',
        'security/ir.model.access.csv',
        'views/inherited_res_partner_views.xml',
        'wizard/google_mybusiness_api_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 108,
}
