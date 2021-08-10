# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Planes Asesoría y Soluciones Informáticas SL
#    Author: Luis Planes
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name':'Beds Model',
    'description': 'Model for Beds',
    'summary': 'Custom Model for Beds',
    'author':'Planes Asesoría y Soluciones Informaticas S.L.',
    'website': 'http://www.planesnet.com',
    'application': True,


    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Website',
    'version': '1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['cs_model','marketing'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/templates_persistent_content.xml',
        'security/ir.model.access.csv',
        'views/res_partner_view.xml',
        'views/ws_view.xml',
        'views/import_data_view.xml',
        'views/product_view.xml',
        'views/sale.xml',
        'views/res_country.xml',
        'views/res_country_state.xml',
        'views/res_partner_brochure_view.xml',
        'views/update_data_country_state.xml',

        'data/data.xml',
        'data/ws.xml',

    ],

    'images':[
            'static/description/splash_screen.png',
    ],
}
