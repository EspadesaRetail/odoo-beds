# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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
import re
from openerp.report.render.rml2pdf import customfonts

class base_config_settings(osv.osv_memory):
    _name = 'custom.config.settings'
    _inherit = 'res.config.settings'
        
    _columns = {
        'allow_partial_payment': fields.boolean('Allow partial payment'),
        'percentage_partial_payment': fields.integer('% partial payment'),
    }
    
    _defaults= {
        'font': lambda self,cr,uid,c: self.pool.get('res.users').browse(cr, uid, uid, c).company_id.font.id,
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: