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
    'name':'Beds Theme',
    'description': 'Tema para la web Beds.es',
    'summary': 'Beds Theme',
    'version':'1.0.1',
    'author':'Planes Asesoría y Soluciones Informaticas S.L.',
    'website': 'http://www.planesnet.com',
    'application': False,

    'data': [
        'views/theme.xml',
        'views/templates.xml',
        'views/templates_remove_products.xml',
        'views/pages.xml',
        'views/snippets.xml',
        'views/templates_promos.xml',



    ],

    'category': 'Theme/Creative',
    'depends': [
        'website','website_sale',
        'cs_model','beds_model','cs_theme','payment_conexflow',
    ],

    'images':[
            'static/description/splash_screen.png',
    ],
}
