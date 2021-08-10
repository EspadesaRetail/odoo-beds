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
    'name': 'Custom Shopping Model',
    'description': 'Custom Shopping Model',
    'summary': 'Custom shopping model',
    'category': 'Website',

    'version': '1.0.1',
    'author': 'Planes Asesoría y Soluciones Informáticas S.L.',
    'depends': ['product', 'sale', 'website_sale','crm','marketing'],
    'data': [
        'views/res_config_view.xml',
        'views/res_partner_view.xml',
        'views/import_data_view.xml',
        'views/product_pricelist_view.xml',
        'views/sale_view.xml',
        'views/res_country.xml',
        'views/ir_attachment_views.xml',
        'views/product_view.xml',
        'views/ir_cron_views.xml',
        'views/mail_templates.xml',
        'views/marketing.xml',
        'views/templates_persistent_content.xml',

        'data/data.xml',
        'data/lang.xml',

        'security/ir.model.access.csv',
        'security/ir.rule.xml',


    ],
    'application': True,


    'images':[
            'static/description/splash_screen.png',
    ],

}
