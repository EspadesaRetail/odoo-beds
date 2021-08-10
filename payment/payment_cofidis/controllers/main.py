# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale

_logger = logging.getLogger(__name__)


class CofidisController(http.Controller):
    _return_url = '/payment/cofidis/return'
    _cancel_url = '/payment/cofidis/cancel'
    _exception_url = '/payment/cofidis/error'
    _reject_url = '/payment/cofidis/reject'

    @http.route([
        '/payment/cofidis/return',
        '/payment/cofidis/confirm',
        '/payment/cofidis/error',
        '/payment/cofidis/reject',
    ], type='http', auth='none')
    def cofidis_return(self, **post):
        """ Cofidis."""
        _logger.info('Cofidis: entering form_feedback with post data %s',
                     pprint.pformat(post))
                     
        # Default return
        return_url = '/'             
        if post:
            # El retorno no se indica en Cofidis. Se gestiona en base al resultado.
            #return_url = post.pop('return_url', '') 

            
            #TODO Pendiente de revisar.
            tx = request.registry['payment.transaction'].form_feedback(
                request.cr, SUPERUSER_ID, post, 'cofidis',
                context=request.context)
                
            if tx:
                return_url = '/payment/cofidis/result/cofidis_result_ok?order_id=%s' % tx.sale_order_id.id
            else:
                return_url = '/payment/cofidis/result/cofidis_result_ko'
            
        _logger.info('RETURN URL %s', str(return_url))    
            
        return werkzeug.utils.redirect(return_url)

    @http.route(
        ['/payment/cofidis/result/<page>'], type='http', auth='user',
        methods=['GET'], website=True)
    def cofidis_result(self, page, **vals):
        try:
            order_id = vals.get('order_id', 0)
            if order_id:
                sale_obj = request.env['sale.order']
                order = sale_obj.browse(int(order_id))
                res = {
                    'order': order,
                }
                return request.render('payment_cofidis.%s' % str(page), res)
            else:
                return request.render('payment_cofidis.cofidis_result_ko')
        except:
            return request.render('website.404')


class WebsiteSale(website_sale):
    @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='json',
                auth="public", website=True)
    def payment_transaction(self, acquirer_id):
        tx_id = super(WebsiteSale, self).payment_transaction(acquirer_id)
        cr, context = request.cr, request.context
        acquirer_obj = request.registry.get('payment.acquirer')
        acquirer = acquirer_obj.browse(
            cr, SUPERUSER_ID, acquirer_id, context=context)
        if acquirer.provider == 'cofidis':
            request.website.sale_reset(context=request.context)
        return tx_id
