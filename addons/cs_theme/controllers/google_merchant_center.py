# -*- coding: utf-8 -*-
import json
import logging
from openerp import SUPERUSER_ID
from openerp import http
from openerp.addons.web.controllers.main import *
from openerp.addons.web.controllers.main import login_redirect
from openerp.addons.website.controllers.main import *
from openerp.addons.website.models.website import slug
from openerp.addons.website_sale.controllers.main import *
from openerp.http import request
from openerp.tools import html_escape as escape
from openerp.tools.translate import _
import werkzeug
_logger = logging.getLogger(__name__)

import re
EXPRESSION_PATTERN = re.compile('(\$\{.+?\})')

class gmc_website(Website):
    
    def render_template_batch(self, cr, uid, template, model, res_ids, context=None, post_process=False):
        """ Render the given template text, replace mako-like expressions ``${expr}``
        with the result of evaluating these expressions with an evaluation context
        containing:

            * ``user``: browse_record of the current user
            * ``object``: browse_record of the document record this mail is
                          related to
            * ``context``: the context passed to the mail composition wizard

        :param str template: the template text to render
        :param str model: model name of the document record this mail is related to
        :param list res_ids: list of record ids
        """
        if context is None:
            context = {}
        results = dict.fromkeys(res_ids, False)

        for res_id in res_ids:
            def merge(match):
                exp = str(match.group()[2:-1]).strip()
                result = eval(exp, {
                    'user': request.registry['res.users'].browse(cr, uid, uid, context=context),
                    'object': request.registry[model].browse(cr, uid, res_id, context=context),
                    'context': dict(context),  # copy context to prevent side-effects of eval
                })
                return result and tools.ustr(result) or ''
            results[res_id] = template and EXPRESSION_PATTERN.sub(merge, template)
        return results



    # Obtener el los parametros del item.    
    def item_param(self, key, value, ns=None):
            
        namespace=''
        if ns:
            namespace = ns+':'
            value = value
            item = '<{2}{0}>{1}</{2}{0}>'.format(key,value,namespace)
            
        return item
            
            
            

    
    
    
    # Obtener el feed de datos para google merchant center / google shopping.
    @http.route('/gmc.xml', type='http', auth="public", website=True)
    def feed_google_merchant_center(self, category=None):
        
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        website = request.website
        product_product_obj = request.registry['product.product']
        iuv = request.registry['ir.ui.view']
        config_obj = request.registry['ir.config_parameter']
        mimetype ='application/xml;charset=utf-8'
        
        
        # Tarifa nacional.
        pricelist = 1
        request.session['pricelist'] = pricelist

        domain=[('website_published','=',True)]
        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]


        #search 
        product_product_ids = product_product_obj.search(cr, uid, domain, context=context)
        products = product_product_obj.browse(cr, uid, product_product_ids, context=context)


        website_url = config_obj.get_param(cr,uid,'web.base.url')

        items=[]
        for product in products:
            pt = product.product_tmpl_id
            if product.lst_price > 0 and (not pt.only_physical_store):

                description = ''
                if pt.website_benefits:
                    description = pt.website_benefits.encode('utf-8')
                    
                description = pt.name.encode('utf-8')

                item = ""
                item += self.item_param('id', product.id,'g')
                item += self.item_param('title', pt.name.encode('utf-8'),'g')
                item += self.item_param('description', description ,'g')
                
                item += self.item_param('link', '{0}/shop/product/{1}'.format(website_url, slug(pt)),'g')
                item += self.item_param('image_link', '{0}/{1}'.format(website_url, website.image_url(pt, 'image')),'g')

                item += self.item_param('condition', "new",'g')
                item += self.item_param('availability', "in stock",'g')
                item += self.item_param('google_product_category', pt.google_product_category,'g')
                item += self.item_param('brand', pt.brand_id.name.encode('utf-8'),'g')
                item += self.item_param('item_group_id', pt.default_code,'g')

                item += self.item_param('price', '{0} EUR'.format(product.lst_price),'g')
                item += self.item_param('sale_price', '{0} EUR'.format(product.discounted_price),'g')
                item += self.item_param('size', product.attribute_value_ids.name,'g')
                item += self.item_param('gtin', product.ean13,'g')
                item += self.item_param('mpn', pt.default_code,'g')
                
                # Shipping
                s = self.item_param('country', 'ES','g')
                s += self.item_param('service', 'Nuestros medios','g')
                s += self.item_param('price', '0 EUR','g')
                item += self.item_param('shipping', s,'g')

                items.append(str(item))

                
        values = {
            'items': items,
        }
        content = iuv.render(cr, uid, 'cs_theme.google_merchant_center_feed', values, context=context)

        return request.make_response(content, [('Content-Type', mimetype)])
    
    def feed_google_merchant_center1(self, category=None):
        cr, uid, context = request.cr, openerp.SUPERUSER_ID, request.context
        product_product_obj = request.registry['product.product']
        iuv = request.registry['ir.ui.view']
        config_obj = request.registry['ir.config_parameter']
        mimetype ='application/xml;charset=utf-8'
        
        
        # Tarifa nacional.
        pricelist = 1
        request.session['pricelist'] = pricelist

        domain=[('website_published','=',True)]
        if category:
            domain += [('public_categ_ids', 'child_of', int(category))]


        #search 
        product_product_ids = product_product_obj.search(cr, uid, domain, context=context)
        products = product_product_obj.browse(cr, uid, product_product_ids, context=context)


        template="""<g:id>${object.default_code}</g:id>"""
        
        #datas = self.render_template_batch(cr, uid, template, "product.template", product_product_ids, context=context)
        #_logger.debug("DATAS: " + str(datas))
        values = {
            #'datas': datas,
            'products': products,
        }
        
        values['website_url'] = config_obj.get_param(cr,uid,'web.base.url')
        
        
        _logger.debug("ANTES DEL RENDER")
        
        content = iuv.render(cr, uid, 'cs_theme.google_merchant_center_feed', values, context=context)

        return request.make_response(content, [('Content-Type', mimetype)])
    
        