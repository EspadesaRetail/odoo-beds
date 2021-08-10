# -*- coding: utf-8 -*-
import logging
import pprint
import werkzeug

from openerp import http, SUPERUSER_ID
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale

_logger = logging.getLogger(__name__)


class StripeController(http.Controller):
    _return_url = '/payment/cf/return'
    _cancel_url = '/payment/cf/cancel'
    _exception_url = '/payment/cf/error'
    _reject_url = '/payment/cf/reject'

    @http.route([
        '/payment/cf/return',
        '/payment/cf/cancel',
        '/payment/cf/error',
        '/payment/cf/reject',
    ], type='http', auth='none')
    def stripe_return(self, **post):
        """ Stripe."""
        _logger.debug('STRIPE_RETURN POST %s',
                     pprint.pformat(post))

        # Default return
        return_url = '/'
        if post:
            # El retorno no se indica en CF. Se gestiona en base al resultado.
            #return_url = post.pop('return_url', '')

            tx = request.registry['payment.transaction'].form_feedback(
                request.cr, SUPERUSER_ID, post, 'stripe',
                context=request.context)

            if tx:
                return_url = '/payment/stripe/result/stripe_result_ok?order_id=%s' % tx.sale_order_id.id
            else:
                return_url = '/payment/stripe/result/stripe_result_ko'

        _logger.info('STRIPE RETURN URL %s', str(return_url))

        return werkzeug.utils.redirect(return_url)



    @http.route(
        ['/payment/stripe/result/<page>'], type='http', auth='none',
        methods=['GET'], website=True)
    def stripe_result(self, page, **vals):

        _logger.debug("STRIPE_RESULT")
        try:
            order_id = vals.get('order_id', 0)
            _logger.debug('STRIPE_RESULT. ORDER_ID:' + str(order_id))
            if order_id:
                sale_obj = request.registry['sale.order']
                order = sale_obj.browse(request.cr, SUPERUSER_ID,int(order_id))
                res = {
                    'order': order,
                }
                return request.render('payment_stripe.%s' % str(page), res)



            else:
                _logger.info('STRIPE RESULT NOOOOOOOOK.')
                return request.render('payment_stripe.stripe_result_ko')
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

        _logger.debug("STRIPE: RESET_SALE_ORDER")
        if acquirer.provider == 'stripe':
            request.website.sale_reset(context=request.context)
        return tx_id
