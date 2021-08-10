##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2015 Planes Asesoría y Soluciones Informáticas SL
#    Author: Alberto Calvo Bazco, Espadesa Retail S.L.
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
    'name':'Beds Corner Brand',
    'description': 'Muestra páginas tipo microsite de las marcas con una serie de productos escogidos',
    'summary': 'Páginas de marcas',
    'version':'1.0.1',
    'author':'Alberto Calvo Bazco, Espadesa Retail S.L.',
    'website': 'http://www.beds.es',
    'application': False,

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/corner_brand_view.xml',
    ],

    'category': 'Brands',
    'depends': [
        'website','website_sale','cs_model','beds_model','beds_theme',
    ],

    'images':[
            'static/description/splash_screen.png',
    ],
}
