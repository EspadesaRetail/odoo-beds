# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Partner and Employees Addons',
    'version': '3.0',
    'category': 'Partner',
    'description': """
Adds to Partner and Employees base modules
==============================================
 Manage data from your Contacts and Employees
==============================================

Addons to manage Partners and Employees.
    """,
    'summary': 'Addons to Manage partners and employees',
    'depends': ['base', 'hr'],
    'data': [
        'views/inherited_res_partner_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 108,
}
