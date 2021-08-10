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


class sale_order(osv.osv):
    _inherit = ['sale.order']

    # Si cambia código de pedido, inicializo el estado para que lo vuelva a recuperar.
    def write(self, cr, uid, ids, vals, context=None):
        if 'beds_pedido' in vals:
            for order in self.browse(cr, uid, ids, context=context):
                if order.beds_pedido and order.beds_pedido != vals['beds_pedido']:
                    vals['beds_estado'] = '0'
                    vals['beds_situacion'] = False

        return super(sale_order, self).write(cr, uid, ids, vals, context=context)

    _columns = {
        'beds_pedido': fields.char("Pedido (bed's)", copy=False, readonly=False),
        'beds_estado': fields.integer("Estado (bed's)", copy=False, readonly=True),
        'beds_fecha_entrega': fields.char("Fecha prevista de entrega", copy=False, readonly=True),
        'beds_situacion': fields.char("Situacion", copy=False, readonly=True),
        'beds_ws_msg': fields.char("WS Mensaje", copy=False, readonly=True),
        'beds_ws_res': fields.char("WS Resultado W", copy=False, readonly=True),
        'beds_pedido_enviado': fields.char("Enviado a (bed's)", copy=False, readonly=False),
    }

    _defaults = {
        'beds_estado': 0,
        'beds_pedido_enviado': None,
    }


    def action_quotation_send(self, cr, uid, ids, context=None):
        order = self.browse(cr, uid, ids[0], context=context)

        #Impide que se genere el email de presupuesto.
        #email_template_edi_sale
        if order.state == 'draft':
            return False

        r = super(sale_order, self).action_quotation_send(cr, uid, ids, context)

        _logger.debug("ACTION_QUOTATION_SEND: " + str(r))

        return r;

class DeliveryCarrier(osv.osv):
    _inherit = "delivery.carrier"

    _columns = {
        'name': fields.char('Delivery Method', required=True, translate=True),
    }

class PaymentAcquirer(osv.Model):
    _inherit = "payment.acquirer"

    _columns = {
        'post_msg': fields.html('Thanks Message', help='Message displayed after having done the payment process.', translate=True),
    }
