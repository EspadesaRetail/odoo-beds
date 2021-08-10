# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import fields, osv
from openerp.tools import html_escape as escape


class res_country(osv.osv):
    _inherit = 'res.country'
    _columns = {
        'sequence': fields.integer('Sequence', required=True, help="The sequence field is used to order the tax lines from the lowest sequences to the higher ones. The order is important if you have a tax with several tax children. In this case, the evaluation order is important."),
    }

    _defaults = {
        'sequence': 1,
    }
    _order = 'sequence'

class country_state(osv.osv):
    _name = 'res.country.state'
    _inherit = ['res.country.state', 'website.seo.metadata']

    _columns = {
        'website_description': fields.html('Descripción web', translate=True),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
