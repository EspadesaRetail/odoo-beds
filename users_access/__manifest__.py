# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Users Addons',
    'version': '3.0',
    'category': 'Users',
    'description': """
Adds to Users base module
==============================================
    Manage access to data from your users.
==============================================

Two ways to manage access from your odoo users.
First, the team that belong user, second, the role
that assign the user to special classification.
    """,
    'summary': 'Addons to Manage users',
    'depends': [],
    'data': [
        'security/users_security.xml',
        'security/ir.model.access.csv',
        'views/inherited_res_users_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 107,
}
