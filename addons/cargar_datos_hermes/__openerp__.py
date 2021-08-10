##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2019 Espadesa Retail S.L.
#    Author: Alberto Calvo Bazco
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
    'name':'Carga de datos a Hermes',
    'description': 'Modulo para el trabajo de atributos de artículos',
    'summary': 'Artículos a cargar en Hermes',
    'version':'1.0.1',
    'author':'Espadesa Retail S.L.',
    'website': 'http://www.beds.es',
    'application': False,

    'data': [
        'views/extraer_textos_views.xml',
    ],

    'category': 'Theme/Creative',
    'depends': [],

    'images':[
            'static/description/splash_screen.png',
    ],
}
