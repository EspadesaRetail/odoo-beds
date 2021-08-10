# -*- coding: utf-8 -*-
from openerp import SUPERUSER_ID

from openerp import api, tools
from openerp.osv import osv, fields, expression

import logging
_logger = logging.getLogger(__name__)



class website_offers(osv.Model):
    _inherit = ["website"]

    # lee los productos para el código 'SO'
    def get_super_offers(self, cr, uid, ids, arg=None, context=None, items_group=3):
        CODE = 'SO'

        return self.get_offers(cr,uid, code=CODE,context=context,items_group=items_group)

    def get_offers(self, cr, uid, code, context, items_group):

        domain=[('code','=',code)]

        obj = self.pool.get('product.offer')
        ids = obj.search(cr, SUPERUSER_ID, domain, limit=1, context=context)

        res = obj.getOffer(cr, SUPERUSER_ID,ids,context=context)

        groups = []
        if res:
            res=res.get(ids[0])

            products = res.get('products',[])

            i=1
            group = []
            for product in products:
                group.append(product)
                i = i + 1
                if i > items_group:
                    i=1
                    groups.append(group)
                    group = []

            if len(group) > 0:
               groups.append(group)

        return groups


    def get_top_valued_products(self, cr, uid, ids, arg=None, context=None, limit=6, items_group=3):
        domain=[('ratingplus','>',0)]

        product_obj = self.pool.get('product.template')
        product_ids = product_obj.search(cr, SUPERUSER_ID, domain, limit=limit, order='ratingplus desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, SUPERUSER_ID, product_ids, context=context)

        groups = []
        i=1
        group = []
        for product in products:
            group.append(product)
            i = i + 1
            if i > items_group:
                i=1
                groups.append(group)
                group = []

        return groups
