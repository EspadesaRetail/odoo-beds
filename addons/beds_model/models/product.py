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

from datetime import datetime
from datetime import timedelta
import json
import logging
from openerp import SUPERUSER_ID
from openerp import workflow
import openerp.addons.decimal_precision as dp
from openerp.osv import fields
from openerp.osv import osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from suds.client import Client
import time
from urllib2 import urlopen
_logger = logging.getLogger(__name__)


class product_template_uncatalog(osv.osv_memory):
    _name = "product.template.uncatalog"
    
    _columns = {
        'products': fields.text('Productos a descatalogar', required=True, translate=True),
    }    
    
    # Permite descatalogar un producto, poniendolo como inactivo.
    def uncatalog_product(self, cr, uid, ids=False, context=None): 
        
        obj = self.pool.get('product.product')
        
        product_ids = []

        if ids:
            products = self.pool.get('product.template.uncatalog').browse(cr, uid,ids)[0].products
            if products:
                products = products.split(" ")
                    
                product_ids = obj.search(cr,uid,[('ean13','in',products)])
                
                # recorrer los productos seleccionados.
                for product in obj.browse(cr, uid, product_ids):
                    product.active = False

                return {
                    'type': 'ir.actions.act_window_close',
                    'tag': 'reload',

                }

        


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
