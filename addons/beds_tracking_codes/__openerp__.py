##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2018 ESPADESA Retail S.L.
#    Author: Alberto Calvo
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
    'name':'Beds Tracking Codes',
    'description': 'Código fuente para los seguimientos de Facebook Pixel',
    'summary': 'Facebook Pixel',
    'version':'1.0.1',
    'author':'ESPADESA Retail S.L.',
    'website': 'http://www.beds.es',

    'data': [
        'views/templates.xml',
    ],
    'category': 'Uncategorized',
    'depends': [
        'website',
    ],
}
