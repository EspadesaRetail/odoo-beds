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
    'name':'Beds Tiendas',
    'description': 'Muestra las páginas asociadas a las tiendas beds',
    'summary': 'Páginas de ubicación de tiends beds',
    'version':'1.0.1',
    'author':'Planes Asesoría y Soluciones Informaticas S.L.',
    'website': 'http://www.planesnet.com',
    'application': False,

    'data': [
        'views/templates.xml',
    ],

    'category': 'Theme/Creative',
    'depends': [
        'website','website_sale','base_geolocalize','cs_model','beds_model','beds_theme',
    ],

    'images':[
            'static/description/splash_screen.png',
    ],
}
