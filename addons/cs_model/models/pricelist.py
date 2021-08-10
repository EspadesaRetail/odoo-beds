# -*- coding: utf-8 -*-
from openerp import api
from openerp.tools.translate import _
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


import logging
import json
_logger = logging.getLogger(__name__)



class product_price_item(osv.osv):
    # Add product fixed price option to pricelist item.
    _inherit = 'product.pricelist.item'


    _columns = {
        'product_price': fields.float('Product price',
            digits_compute= dp.get_precision('Product Price'), help='Specify the fixed product price'),
        'product_discount': fields.float('Product discount (%)',
            digits_compute= dp.get_precision('Discount'), help='Specify the fixed product discount'),
        'product_tax_percentage': fields.float('Product Tax (%)',
            digits_compute= dp.get_precision('Account'), help='Specify the tax percentege for product'),
        'date_last_update': fields.datetime('Última actualización de precios',),
    }

    _defaults = {
        'product_price': 0,
        'product_discount': 0,
        'date_last_update' : lambda *a: time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
    }



class product_pricelist(osv.osv):
    _inherit = 'product.pricelist'



    # Rutina de cálculo de precios.
    def price_rule_get_multi(self, cr, uid, ids, products_by_qty_by_partner, context=None):
        """multi products 'price_get'.
           @param ids: pricelist_id
           @param products_by_qty:
           @param partner:
           @param context: {
             'date': Date of the pricelist (%Y-%m-%d),}
           @return: a dict of dict with product_id as key and a dict 'price by pricelist' as value
        """

        results = super(product_pricelist, self).price_rule_get_multi(cr, uid, ids, products_by_qty_by_partner, context)


        _logger.debug("SUPER PRICE_RULE_GET_MULTI: " + str(results))
        _logger.debug("SUPER ITEMS: " + str(results.items()))

        product_obj = self.pool.get('product.product')
        product_ids = [product_id for product_id,subres in results.items()]
        products = product_obj.browse(cr,uid,product_ids)

        for product in products:
            #results[product.id][1] = (product.lst_price,None)
            results[product.id][1] = (product.price,None)


        _logger.debug("PRICE_RULE_GET_MULTI: " + str(results))

        return results
