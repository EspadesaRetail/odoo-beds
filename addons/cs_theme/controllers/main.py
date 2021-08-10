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
import math
_logger = logging.getLogger(__name__)

from openerp.addons.cs_model.models.product import *
from openerp.addons.website_sale.models.product import product_public_category
import re
from time import sleep


PPG = 9 # Products Per Page
PPR = 3  # Products Per Row




def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(pav):

    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', str(pav.sequence)) ]





class table_compute1(object):
    def __init__(self):
        self.table = {}

    def _check_place(self, posx, posy, sizex, sizey):
        res = True
        for y in range(sizey):
            for x in range(sizex):
                if posx + x >= PPR:
                    res = False
                    break
                row = self.table.setdefault(posy + y, {})
                if row.setdefault(posx + x) is not None:
                    res = False
                    break
            for x in range(PPR):
                self.table[posy + y].setdefault(x, None)
        return res

    def process(self, products=[], ppg=PPG, ppr=PPR):
        # Compute products positions on the grid
        minpos = 0
        index = 0
        maxy = 0
        for p in products:
            x = min(max(p.website_size_x, 1), ppr)
            y = min(max(p.website_size_y, 1), ppr)
            if index >= ppg:
                x = y = 1

            pos = minpos
            while not self._check_place(pos % ppr, pos / ppr, x, y):
                pos += 1
            # if 21st products (index 20) and the last line is full (PPR products in it), break
            # (pos + 1.0) / PPR is the line where the product would be inserted
            # maxy is the number of existing lines
            # + 1.0 is because pos begins at 0, thus pos 20 is actually the 21st block
            # and to force python to not round the division operation
            if index >= ppg and ((pos + 1.0) / ppr) > maxy:
                break

            if x == 1 and y == 1:   # simple heuristic for CPU optimization
                minpos = pos / ppr

            for y2 in range(y):
                for x2 in range(x):
                    self.table[(pos / ppr) + y2][(pos % ppr) + x2] = False
            self.table[pos / ppr][pos % ppr] = {
                'product': p, 'x':x, 'y': y,
                'class': " ".join(map(lambda x: x.html_class or '', p.website_style_ids))
            }
            if index <= ppg:
                maxy = max(maxy, y + (pos / ppr))
            index += 1

        # Format table according to HTML needs
        rows = self.table.items()
        rows.sort()
        rows = map(lambda x: x[1], rows)
        for col in range(len(rows)):
            cols = rows[col].items()
            cols.sort()
            x += len(cols)
            rows[col] = [c for c in map(lambda x: x[1], cols) if c != False]

        return rows

        # TODO keep with input type hidden


# Calcula los precios y descuentos para cada una de las variantes.
def get_attribute_value_ids1(product):
    cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
    currency_obj = pool['res.currency']
    attribute_value_ids = []
    visible_attrs = set(l.attribute_id.id
                        for l in product.attribute_line_ids
                        if len(l.value_ids) > 1)


    # Crea una lista con todos los productos y guarda los valores:
    #[product][Identificador del atributo][datos], donde datos es:
    #[1] precio aplicado el descuento.,
    #[2] precio tarifa,
    #[3] descuento,

    #_logger.debug("GET ATTRIBUTE VALUE IDS:" + str(context))

    attribute_value_ids = [[p.id, [v.id for v in p.attribute_value_ids if v.attribute_id.id in visible_attrs],
        p.price, p.lst_price, p.lst_discount, p.lst_discount_offer
    ] for p in product.product_variant_ids]

    return attribute_value_ids

# Calcula los precios y descuentos para cada una de las variantes.
def get_attribute_value_ids_packs(pack, product):
    cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

    visible_attrs = set(l.attribute_id.id
                        for l in product.attribute_line_ids
                        if len(l.value_ids) > 1)


    # Crea una lista con todos los productos y guarda los valores:
    #[product][Identificador del atributo][datos], donde datos es:
    #[1] precio aplicado el descuento.,
    #[2] precio tarifa,
    #[3] descuento,

    #_logger.debug("GET ATTRIBUTE VALUE IDS:" + str(context))

    Offer = pool['product.offer']

    attribute_value_ids = []
    for p in product.product_variant_ids:

        # Caso general
        # Precio tarifa.
        precio_promo = p.price

        if pack.offer_id and pack.offer_id.active_now:

            # Caso pack + regalo (type='pack')
            if pack.offer_id.offer_type == 'pack':
                # El colchón se cobra, el resto no.
                category = product.public_categ_ids
                if category:
                    category = category[0]
                if category and category.parent_id:
                    category = category.parent_id
                if category and category.name != "COLCHONES":
                    """
                    offer_id = Offer.search(cr,uid,[('pack_ids','in', pack.id)], limit=1)
                    if offer_id:
                        offer_id = Offer.browse(cr,uid,offer_id)
                        if offer_id.active:
                            precio_promo = 0         # Promoción pack colchón + base de regalo.
                    """
                    precio_promo = 0         # Promoción pack colchón + base de regalo.

            # Caso pack + dto  (type='pack-dto')
            elif pack.offer_id.offer_type == 'pack-dto':
                precio_promo = precio_promo * (100 - pack.offer_id.additional_dto) /100

        attribute_value_ids += [[p.id, [v.id for v in p.attribute_value_ids if v.attribute_id.id in visible_attrs],
            precio_promo, p.lst_price, p.lst_discount, p.lst_discount_offer]]

    return attribute_value_ids




class QueryURL1(object):
    def __init__(self, path='', ** args):
        self.path = path
        self.args = args


    def __call__(self, path=None, category=None, brand=None, ** kw):

        l = []

        if category:
            if isinstance(category, product_public_category):
                path = '/shop/category/' + slug(category)

            elif isinstance(category, product_public_category_brand):
                path = '/shop/category/' + slug(category.public_category)

            if brand:
                l.append(werkzeug.url_encode([('brand', brand.id)]))


        elif brand:
            path = '/shop/brand/' + slug(brand)
            kw.pop('brand', None) #quitar el parámetro brand, ya que no hace falta especificarlo.



        if not path:
            path = self.path

        for k, v in self.args.items():
            kw.setdefault(k, v)

        #_logger.debug("PARAMETERS KW:" + str(kw))

        for k, v in kw.items():
            if v:
                if isinstance(v, list) or isinstance(v, set):
                    l.append(werkzeug.url_encode([(k, i) for i in v]))
                else:
                    l.append(werkzeug.url_encode([(k, v)]))

        if l:
            path += '?' + '&'.join(l)
        return path


def get_pricelist():
    cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

    pricelist = request.session.get("pricelist", 1)

    if type(pricelist) is int:
        obj = pool['product.pricelist']
        pricelist = obj.browse(cr, uid,[pricelist])[0]

    return pricelist





class cs_website_sale(website_sale):

    def get_attribute_value_ids(self, product):
        return get_attribute_value_ids1(product)

    def get_pack_attribute_value_ids(self, pack, product):
        return get_attribute_value_ids_packs(pack, product)

    def get_pricelist(self):
        pricelist = get_pricelist()
        return pricelist


    @http.route(['/shop/cart'], type='http', auth="public", website=True)
    def cart(self, **post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        pricelist = request.session.get("pricelist")
        context['pricelist'] = pricelist


        r = super(cs_website_sale, self).cart(**post)


        order = request.website.sale_get_order()

        # Mostrar si es necesario la posibilidad de recoger colchones viejos.
        r.qcontext['remove_old_products'] = order and order.allow_remove_old_products

        # No permitir cambiar la localización
        r.qcontext['zip_code_lock'] = True


        return r

    # Indica que se solicita recoger los produtos viejos, colchones y bases.
    @http.route(['/shop/set_remove_old_products'], type='json', auth="public", methods=['POST'], website=True)
    def set_remove_old_products(self, remove_old_products, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        #_logger.debug("REMOVE OLD PRODUCTS: " + str(remove_old_products))
        order = request.website.sale_get_order()
        if order:
            order.write({'remove_old_products':remove_old_products})
            order.update_remove_old_products()
            #_logger.debug("Datos a grabar: " + order.name + " " +str({'remove_old_products':remove_old_products}))
            return True
        return False

    # Modificar el estándar ya que es necesario enviar el descuento.
    @http.route(['/shop/get_unit_price'], type='json', auth="public", methods=['POST'], website=True)
    def get_unit_price(self, product_ids, add_qty, use_order_pricelist=False, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        products = pool['product.product'].browse(cr, uid, product_ids, context=context)
        partner = pool['res.users'].browse(cr, uid, uid, context=context).partner_id
        if use_order_pricelist:
            #_logger.debug("USER ORDER PRICE LIST")
            pricelist_id = request.session.get('sale_order_code_pricelist_id') or partner.property_product_pricelist.id
        else:
            #_logger.debug("NO USER ORDER PRICE LIST")
            pricelist_id = partner.property_product_pricelist.id

        if not pricelist_id:
            pricelist_id = request.session.get('pricelist')
        context['pricelist'] = pricelist_id

        #_logger.debug("_GET_UNIT_PRICE PRICELIST_ID:" + str(pricelist_id))
        #_logger.debug("_GET_UNIT_PRICE PRICELIST_ID PRODUCTS:" + str(products))

        prices = pool['product.pricelist'].price_rule_get_multi(cr, uid, [pricelist_id], [(product, add_qty, partner) for product in products], context=context)


        #_logger.debug("_GET_UNIT_PRICE PRICES:" + str(prices))
        return {product_id: prices[product_id][pricelist_id][0] for product_id in product_ids}


    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', ** kwargs):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        r = super(cs_website_sale, self).product(product, category, search,  ** kwargs)


        # Comprobar si el producto está desactivado y reemplazado por otro.
        if product.replace_by:
            return request.redirect("/shop/product/%s" % slug(product.replace_by), code=301)

        # Comprobar si el producto está metido dentro de un grupo de productos.
        # y dicho producto agrupado está publicado.
        if product.product_group_id and product.product_group_id.website_published:
            return request.redirect("/shop/product/%s" % slug(product.product_group_id), code=301)

        attrib_set = request.session.get("attrib_set",False)

        r.qcontext['image_url'] = product.image_url

        #Cargar los atributos por defecto de todas las categorías públicas.
        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        # Inicializar la medida seleccionada anteriormente.
        if not attrib_set:
            attrib_set = []
            for c in categs:
                if c.attribute_default_value:
                    attrib_set += [c.attribute_default_value.id]

        r.qcontext['attrib_set'] = set(attrib_set)

        r.qcontext['get_pack_attribute_value_ids'] = self.get_pack_attribute_value_ids

        # Indica que se debe mostrar el carrito de compra.
        r.qcontext['show_cart'] = True

        if 'zip_code_state' in request.session:
            r.qcontext['zip_code'] = request.session['zip_code']
            r.qcontext['zip_code_state'] = request.session['zip_code_state']

        # Packs
        r.qcontext['packs'] = [x for x in product.pack_ids if x.active_now]

        # Obtener la campaña activa.
        Offer = pool['product.offer']
        r.qcontext['offer'] = Offer.get_first_offer(cr, uid, context)

        return r

    def shop_category(self, page=0, category=None,  ** post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        search = None
        brand = None
        if 'brand' in post.keys() and post['brand']:
            brand = pool['product.brand'].browse(cr, uid, int(post['brand']), context=context)[0]

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])


        domain = self._get_search_domain(search, category, attrib_values)
        #keep = QueryURL1('/shop', search=search, attrib=attrib_list)
        keep = QueryURL1('/shop', search=search)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = pricelist
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

        url = "/shop"

        if brand:
            domain += [('brand_id', '=', int(brand))]

        product_obj = pool.get('product.template')

        product_count = product_obj.search_count(cr, uid, domain, context=context)


        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)

        if attrib_list:
            post['attrib'] = attrib_list
        product_ids = product_obj.search(cr, uid, domain, order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        # Obtener todas las categorías padre de productos.
        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)


        # Categorías de productos, pero filtrando por los productos.
        category_domain = []

        if category:
            category_domain += [('parent_id', '=', category.id)]

        """
        # Muestra las subcategorias de todos los productos.
        product_category_ids = []
        for product in products:
            for x in product.public_categ_ids:
                product_category_ids.append(x.id)

        # Mostrar en el detalle, sólo las subcategorías con los productos seleccionados.
        product_category_ids = list(set(product_category_ids))
        category_domain += [('id', 'in', product_category_ids)]
        """

        category_ids = category_obj.search(cr, uid, category_domain, context=context)
        #_logger.info("CATEGORY IDS" + str(category_ids))

        detail_content = category_obj.browse(cr, uid, category_ids, context=context)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)


        # define data of template.
        title = None
        content = category
        if brand and category:
            obj = request.registry['product.public.category.brand']
            dom = [('public_category', '=', category.id), ('brand', '=', brand.id)]
            ids = obj.search(cr, uid, dom, context=context)
            if ids:
                content = obj.browse(cr, uid, ids, context=context)[0]
                title = category.name + ' de ' + brand.name

        # Obtener la campaña activa.
        Offer = pool['product.offer']
        offer = Offer.get_first_offer(cr, uid, context)


        values = {
            'title': title,
            'content': content,
            'detail_content': detail_content,
            'brand': brand,
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': set(attrib_set),
            'pager': None,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute1().process(products),
            'rows': PPR,
            'styles': styles,
            'categories': categs,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib', i) for i in attribs]),
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'get_pack_attribute_value_ids': self.get_pack_attribute_value_ids,
            'offer': offer,
        }

        if content:
            values.update({'main_object': content})


        return request.website.render("cs_theme.categories", values)

    def shop_subcategory(self, page=0, category=None, ** post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        def round_filter_value(x):
            return int(math.ceil(x / 100.0)) * 100

        # Formato de visualización de productos, en grid o en lista.
        product_grid = request.session.get("product_grid", True)

        ## Filters
        filters = request.session.get('filters',{})
        filter = filters.get('price', False)

        if not filter:
            filters['price'] = {
                'min' : 0,
                'max' : 0,
                'step' : 100,
                'value' : False,
            }

        # la subcategoria es obligatoria
        parent = category.parent_id

        search = None
        brand = None
        if 'brand' in post.keys() and post['brand']:
            brand = pool['product.brand'].browse(cr, uid, int(post['brand']), context=context)[0]

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        # guardar el attrib_set en la session, para poder leerlo en la visualización del producto.
        request.session["attrib_set"] = set(attrib_set)


        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL1('/shop', search=search)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = pricelist
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        url = "/shop"

        if brand:
            domain += [('brand_id', '=', int(brand))]


        #_logger.debug("Domain products: %s" % str(domain))

        product_count = product_obj.search_count(cr, uid, domain, context=context)
        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)
        if attrib_list:
            post['attrib'] = attrib_list
        pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
        product_ids = product_obj.search(cr, uid, domain, limit=PPG, offset=pager['offset'], order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        # Categorías para mostrar en el lateral.
        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)


        # Categorías de productos, pero filtrando por los productos seleccinados.
        category_domain = []
        if category:
            category_domain = [('parent_id', '=', category.id)]


        # Mostrar todas las categorías, aunque no tengan productos.
        #product_category_ids = []
        #for product in products:
        #    for x in product.public_categ_ids:
        #        product_category_ids.append(x.id)
        #product_category_ids = list(set(product_category_ids))
        #category_domain = [('id', 'in', product_category_ids)]

        category_ids = category_obj.search(cr, uid, category_domain, context=context)
        detail_content = category_obj.browse(cr, uid, category_ids, context=context)

        #_logger.debug("CATEGORY ATTRIBUTES:" + str(parent.attribute_ids))
        attributes_domain = []
        if parent:
            aids = []
            for a in parent.attribute_ids:
                aids.append(a.id)

            attributes_domain = [('id','in',aids)]

        if parent:
            if len(attrib_set)==0:
                if category.attribute_default_value:
                    attrib_set = [category.attribute_default_value.id]
                else:
                    attrib_set = [parent.attribute_default_value.id]

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, attributes_domain, context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        """
        Calcular los valores de los atributos, que pueden tener los productos que se van a mostrar.
        Crear un dictionary, con todos los atributos y para cada uno de ellos con todos los valores.
        """
        attributes_values={}

        for a in attributes:
            attributes_values.update({a.id:[]})

        #_logger.debug("ATTRIBUTES_VALUES: " + str(attributes_values))
        if len(attributes_values)>0:
            for pt in products:
                for p in pt.product_variant_ids:
                    for v in p.attribute_value_ids:
                        if v.attribute_id.id in attributes_values and v not in attributes_values[v.attribute_id.id]:
                            attributes_values[v.attribute_id.id].append(v)

        #Ordenar los valores de los atributos.
        for k in attributes_values.keys():
            attributes_values[k].sort(key=natural_keys)


        #Si no hay valores quitar el atributo.
        d = []
        av={}
        a=[]
        for k in attributes_values.keys():
            if len(attributes_values[k])>0:
                av[k] = attributes_values[k]
                d.append(int(k))
        attributes_values = av
        attributes = attributes_obj.browse(cr, uid, d, context=context)



        # define data of template.
        title = None
        content = category
        if brand and category:
            obj = request.registry['product.public.category.brand']
            dom = [('public_category', '=', category.id), ('brand', '=', brand.id)]
            ids = obj.search(cr, uid, dom, context=context)
            if ids:
                content = obj.browse(cr, uid, ids, context=context)[0]
                title = category.name + ' de ' + brand.name

        # Calcular los límites del filtro.
        filter = filters.get('price')
        filter_price = float(filter['value'])
        filter_max = 0

        filter_products=[]
        for pt in products:
            for p in pt.product_variant_ids:
                for v in p.attribute_value_ids:
                    if v.id in attrib_set:
                        if p.price >= filter_max:
                            filter_max = p.price

                        if not filter_price or p.price <= filter_price:
                            filter_products.append(p.product_tmpl_id.id)

        # Actualizar el filtro.
        filters['price']['max'] = int(round_filter_value(filter_max))

        if filters['price']['value'] and filters['price']['value'] > filters['price']['max']:
            filters['price']['value'] = filters['price']['max']

        # Sólo aplicar el fitro si es necesario (value < max)
        if filter['value'] and filter['value'] < filter['max']:

            filter_products =list(set(filter_products))
            _logger.debug("FILTER PRODUCTS: " + str(filter_products))

            # Update product list
            products = product_obj.browse(cr, uid, filter_products, context=context)
            product_count = len(filter_products)

        # Save the filters
        # Se actualiza en cualquier caso, ya que el filtro siempre aparece.
        request.session['filters'] = filters
        _logger.debug("Save filters :" + str(request.session['filters']))



        bins = None
        if product_grid:
            bins = table_compute1().process(products)

        # Obtener la campaña activa.
        Offer = pool['product.offer']
        offer = Offer.get_first_offer(cr, uid, context)


        values = {
            'title': title,
            'content': content,
            'brand': brand,
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': set(attrib_set),
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': bins,
            'rows': PPR,
            'styles': styles,
            'categories': categs,
            'detail_content': detail_content,
            'attributes': attributes,
            'attributes_values': attributes_values,    # attributes_values[attribute][
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib', i) for i in attribs]),
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'get_pack_attribute_value_ids': self.get_pack_attribute_value_ids,
            'filters': filters,
            'offer': offer,
        }
        if content:
            values.update({'main_object': content})


        return values


    def shop_products(self, product_ids , ** post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        keep = QueryURL1('/shop', search=None)

        # Formato de visualización de productos, en grid o en lista.
        product_grid = request.session.get("product_grid", True)

        page=None
        category=None
        brand = None

        domain = [('id','in',product_ids)]

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = pricelist
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        url = "/shop"

        product_count = product_obj.search_count(cr, uid, domain, context=context)

        pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
        product_ids = product_obj.search(cr, uid, domain, offset=pager['offset'], order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)


        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        # guardar el attrib_set en la session, para poder leerlo en la visualización del producto.
        request.session["attrib_set"] = set(attrib_set)


        # Obtener los atributos de los productos.

        category_ids = [product.categ_id.id for product in products]

        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)
        detail_content = category_obj.browse(cr, uid, category_ids, context=context)

        attributes_domain = []
        aids = []
        for categ in categs:
            for a in categ.attribute_ids:
                aids.append(a.id)

            attributes_domain = [('id','in',aids)]

        for categ in categs:
            if categ.attribute_default_value:
                attrib_set = [categ.attribute_default_value.id]

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, attributes_domain, context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        """
        Calcular los valores de los atributos, que pueden tener los productos que se van a mostrar.
        Crear un dictionary, con todos los atributos y para cada uno de ellos con todos los valores.
        """
        attributes_values={}

        for a in attributes:
            attributes_values.update({a.id:[]})

        #_logger.debug("ATTRIBUTES_VALUES: " + str(attributes_values))
        if len(attributes_values)>0:
            for pt in products:
                for p in pt.product_variant_ids:
                    for v in p.attribute_value_ids:
                        if v.attribute_id.id in attributes_values and v not in attributes_values[v.attribute_id.id]:
                            attributes_values[v.attribute_id.id].append(v)

        #Ordenar los valores de los atributos.
        for k in attributes_values.keys():
            attributes_values[k].sort(key=natural_keys)


        #Si no hay valores quitar el atributo.
        d = []
        av={}
        a=[]
        for k in attributes_values.keys():
            if len(attributes_values[k])>0:
                av[k] = attributes_values[k]
                d.append(int(k))
        attributes_values = av
        attributes = attributes_obj.browse(cr, uid, d, context=context)



        # define data of template.
        title = None
        content = category
        if brand and category:
            obj = request.registry['product.public.category.brand']
            dom = [('public_category', '=', category.id), ('brand', '=', brand.id)]
            ids = obj.search(cr, uid, dom, context=context)
            if ids:
                content = obj.browse(cr, uid, ids, context=context)[0]
                title = category.name + ' de ' + brand.name


        # define data of template.
        title = None
        content = category

        bins = None
        if product_grid:
            bins = table_compute1().process(products,50,3)

        # Obtener la campaña activa.
        Offer = pool['product.offer']
        offer = Offer.get_first_offer(cr, uid, context)

        values = {
            'title': title,
            'content': content,
            'brand': None,
            'search': None,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': set(attrib_set),
            'pager': None,
            'pricelist': pricelist,
            'products': products,
            'bins': bins,
            'rows': PPR,
            'styles': styles,
            'categories': None,
            'detail_content':products,
            'attributes': attributes,
            'attributes_values': attributes_values,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib', i) for i in attribs]),
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'get_pack_attribute_value_ids': self.get_pack_attribute_value_ids,
            'filters' : None,
            'offer': offer,
        }
        if content:
            values.update({'main_object': content})

        

        return values


    def shop_search(self, page=0, search='', ** post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        category = None
        brand = None

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        domain = self._get_search_domain(search, category, attrib_values)

        #keep = QueryURL1('/shop', search=search, attrib=attrib_list)
        keep = QueryURL1('/shop', search=search)

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = pricelist
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        url = "/shop"

        product_count = product_obj.search_count(cr, uid, domain, context=context)
        if search:
            post["search"] = search
        if category:
            category = pool['product.public.category'].browse(cr, uid, int(category), context=context)
            url = "/shop/category/%s" % slug(category)
        if attrib_list:
            post['attrib'] = attrib_list
        pager = request.website.pager(url=url, total=product_count, page=page, step=PPG, scope=7, url_args=post)
        product_ids = product_obj.search(cr, uid, domain, offset=pager['offset'], order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        style_obj = pool['product.style']
        style_ids = style_obj.search(cr, uid, [], context=context)
        styles = style_obj.browse(cr, uid, style_ids, context=context)

        # Categorías para mostrar en el lateral.
        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)


        product_category_ids = []
        for product in products:
            for x in product.public_categ_ids:
                product_category_ids.append(x.id)

        product_category_ids = list(set(product_category_ids))

        category_domain = [('id', 'in', product_category_ids)]
        category_ids = category_obj.search(cr, uid, category_domain, context=context)
        detail_content = category_obj.browse(cr, uid, category_ids, context=context)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)


        values = {
            'title': None,
            'content': None,
            'brand': None,
            'search': search,
            'category': None,
            'attrib_values': attrib_values,
            'attrib_set': set(attrib_set),
            'pager': pager,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute1().process(products),
            'rows': PPR,
            'styles': styles,
            'categories': categs,
            'detail_content': None,
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib', i) for i in attribs]),
            'main_object': None,
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'get_pack_attribute_value_ids': self.get_pack_attribute_value_ids,
        }
        return request.website.render("cs_theme.search", values)


    @http.route([
                '/shop/brands',
                '/shop/brand/<model("product.brand"):brand>',
                '/shop/brand/<model("product.brand"):brand>/page/<int:page>'
                ], type='http', auth="public", website=True)
    def shop_brand(self, page=0, brand=None, search='', website=True, ** post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [map(int, v.split("-")) for v in attrib_list if v]
        attrib_set = set([v[1] for v in attrib_values])

        #domain = self._get_search_domain(search, category, attrib_values)
        domain = request.website.sale_product_domain()

        #keep = QueryURL1('/shop/brands', search=search, attrib=attrib_list)
        keep = QueryURL1('/shop/brands', search=search)

        url = "/shop"

        if brand:
            brand = pool['product.brand'].browse(cr, uid, int(brand), context=context)
            domain += [('brand_id', '=', int(brand))]
            url = "/shop/brand/%s"

        if not context.get('pricelist'):
            pricelist = self.get_pricelist()
            context['pricelist'] = pricelist
        else:
            pricelist = pool.get('product.pricelist').browse(cr, uid, context['pricelist'], context)

        product_obj = pool.get('product.template')

        product_count = product_obj.search_count(cr, uid, domain, context=context)

        if search:
            post["search"] = search



        if attrib_list:
            post['attrib'] = attrib_list
        product_ids = product_obj.search(cr, uid, domain, order='website_published desc, website_sequence desc', context=context)
        products = product_obj.browse(cr, uid, product_ids, context=context)

        # obtener las categorías a mostrar en la web.
        category_domain = [('parent_id', '=', False)]
        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, category_domain, context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        attributes_obj = request.registry['product.attribute']
        attributes_ids = attributes_obj.search(cr, uid, [], context=context)
        attributes = attributes_obj.browse(cr, uid, attributes_ids, context=context)

        from_currency = pool.get('product.price.type')._get_field_currency(cr, uid, 'list_price', context)
        to_currency = pricelist.currency_id
        compute_currency = lambda price: pool['res.currency']._compute(cr, uid, from_currency, to_currency, price, context=context)

        # Obtener las categorías Padre de los productos para poder mostrarlas.
        product_category_ids = []
        for product in products:
            for x in product.public_categ_ids:
                product_category_ids.append(x.id)

        product_category_ids = list(set(product_category_ids))
        category_domain += [('child_id', 'in', product_category_ids)]
        category_ids = category_obj.search(cr, uid, category_domain, context=context)


        # Cargar un diccionario, ya que luego se puede reemplazar algún objeto.
        detail_content = dict.fromkeys(category_ids, False)
        for o in category_obj.browse(cr, uid, category_ids, context=context):
            detail_content[o.id] = o

        #_logger.debug("DETAIL CONTENT:" + str(detail_content))

        # Si no hay una marca concreta, se cargan todas y se utiliza la plantilla cs_theme.brands
        brands = None
        if not brand:
            brand_obj = pool['product.brand']
            brand_ids = brand_obj.search(cr, SUPERUSER_ID, [], context=context)


            #_logger.info("BRANDS:" + str(brand_ids))
            brands = brand_obj.browse(cr, SUPERUSER_ID, brand_ids, context=context)
            #_logger.info("BRANDS:" + str(brands))

        # Se ha seleccionado una marca concreta.
        else:
            # Reemplazar las categorias por la categorias por marca si existen.
            obj = request.registry['product.public.category.brand']
            dom = [('brand', '=', brand.id), ('public_category', 'in', category_ids)]
            ids = obj.search(cr, SUPERUSER_ID, dom, context=context)
            if ids:

                #_logger.debug("CATEGORIAS CON MARCAS:" + str(ids))

                for o in obj.browse(cr, SUPERUSER_ID, ids, context=context):
                    detail_content[o.public_category.id] = o

        # Obtener la campaña activa.
        Offer = pool['product.offer']
        offer = Offer.get_first_offer(cr, uid, context)
        values = {
            'search': search,
            'brand': brand,
            'brands': brands,
            'attrib_values': attrib_values,
            'attrib_set': set(attrib_set),
            'pager': None,
            'pricelist': pricelist,
            'products': products,
            'bins': table_compute1().process(products),
            'rows': PPR,
            'styles': None,
            'categories': categs,
            'detail_content': detail_content.values(),
            'attributes': attributes,
            'compute_currency': compute_currency,
            'keep': keep,
            'style_in_product': lambda style, product: style.id in [s.id for s in product.website_style_ids],
            'attrib_encode': lambda attribs: werkzeug.url_encode([('attrib', i) for i in attribs]),
            'get_attribute_value_ids': self.get_attribute_value_ids,
            'get_pack_attribute_value_ids': self.get_pack_attribute_value_ids,
            'offer': offer,
        }


        if brand:
            values.update({'main_object': brand})
            return request.website.render("cs_theme.detail_brand", values)
        else:
            return request.website.render("cs_theme.brands", values)




    @http.route()
    def shop(self, page=0, category=None, search='', ** post):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        #r = super(cs_website_sale, self).shop(page, category, search, **post)

        if not category:
            return self.shop_search(page, search, ** post)

        if category.parent_id or not category.child_id:
            values = self.shop_subcategory(page, category, ** post)
            return request.website.render("cs_theme.subcategories", values)


        if not category.parent_id:
            #_logger.debug("CATEGORY TEMPLATE")
            return self.shop_category(page, category, ** post)


        else:
            #_logger.debug("SEARCH TEMPLATE")
            return self.shop_search(page, search, ** post)

    # Resetear la localización.
    @http.route(['/location/js_reset'], type='json', auth="public", website=True)
    def location_js_reset(self, **kwargs):
        request.session['zip_code'] = None
        request.session['zip_code_state'] = None
        return

    @http.route(['/location/modal'], type='json', auth="public", methods=['POST'], website=True)
    def modal(self, **kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        pricelist = self.get_pricelist()
        if not context.get('pricelist'):
            context['pricelist'] = int(pricelist)

        return request.website._render("cs_theme.modal_zip_code", {
                'zip_code': request.session and request.session.get("zip_code", None),
                'zip_code_state': request.session and request.session.get("zip_code_state", None),
            })




    # Identificar la tarifa a aplicar en función del código postal.
    # Se dan 3 Tarifas:
    # Peninsula
    # Canarias
    # Baleares
    @http.route(['/shop/set_zip_code'], type='json', auth="public", website=True)
    def set_zip_code(self, zip_code, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        pricelist = False

        zip_code = zip_code.strip()
        if(len(zip_code)==0):
            #_logger.debug("No zip code specified")
            return False;


        obj = request.registry['product.pricelist']
        state_obj = request.registry['res.country.state']

        zip_code = '{:05.0f}'.format(int(zip_code))

        if not (0 < int(zip_code[:2]) <= 50):
            return False;

        context['zip_code'] = zip_code
        request.session['zip_code'] = zip_code

        z = int(zip_code[:2])
        state_ids = state_obj.search(cr, SUPERUSER_ID, [('code', '=', z)])
        state = False
        request.session['zip_code_state'] = 'Introduce el código postal'
        if state_ids:
            state = state_obj.browse(cr, SUPERUSER_ID, state_ids)[0].name
            request.session['zip_code_state'] = state


        code = 'P'
        if zip_code[:2] in ['35','38']:
            code = 'C'
        if zip_code[:2] in ['07']:
            code = 'B'

        ids = obj.search(cr, SUPERUSER_ID, [('code', '=', code)])
        if ids:
            pricelist = ids[0]
            context['pricelist'] = pricelist
            request.session['pricelist'] = pricelist

        order = request.website.sale_get_order(force_create=1,update_pricelist=True, context=context)
        values = {'pricelist_id': pricelist}
        values.update(order.onchange_pricelist_id(pricelist, None)['value'])
        order.write(values)
        for line in order.order_line:
            if line.exists():
                order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)

        values = {
            'zip' : zip_code,
            'zip_code' : zip_code,
            'zip_code_state': state,
            'pricelist' : pricelist,
        }

        _logger.info("Setting zip code to [%s]" % zip_code)

        return values


    # Modificar los valores obligatorios del formulario de pedido.
    custom_mandatory_billing_fields = ["name1","name2", "vat", "vat_subjected", "street_type", "street_name", "street_number","city","zip"]
    custom_optional_billing_fields = ["street_esc","street_piso","street_puerta"]
    custom_mandatory_shipping_fields = ["street_type", "street_name", "street_number","city","zip"]
    custom_optional_shipping_fields = ["street_esc","street_piso","street_puerta"]


    def _get_mandatory_billing_fields(self):
        r = super(cs_website_sale, self)._get_mandatory_billing_fields()
        return self.custom_mandatory_billing_fields + r

    def _get_optional_billing_fields(self):
        r = super(cs_website_sale, self)._get_optional_billing_fields()
        return self.custom_optional_billing_fields + r

    def _get_mandatory_shipping_fields(self):
        r = super(cs_website_sale, self)._get_mandatory_shipping_fields()
        return self.custom_mandatory_shipping_fields + r

    def _get_optional_shipping_fields(self):
        r = super(cs_website_sale, self)._get_optional_shipping_fields()
        return self.custom_optional_shipping_fields + r



    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        order = request.website.sale_get_order(context=context)


        if not order:
            return request.redirect("/shop")

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        # Obtener los valores del formulario.
        values = self.checkout_values(post)

        values["error"] = self.checkout_form_validate(order, values["checkout"])
        if values["error"]:
            return request.website.render("website_sale.checkout", values)

        self.checkout_form_save(values["checkout"])

        request.session['sale_last_order_id'] = order.id

        #request.website.sale_get_order(update_pricelist=True, context=context)

        return request.redirect("/shop/payment")

    def checkout_form_save(self, checkout):
        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        _logger.debug("CHECK OUT FORM SAVE: " +str(checkout))

        order = request.website.sale_get_order(force_create=1, update_pricelist=False, context=context)

        orm_partner = registry.get('res.partner')
        orm_user = registry.get('res.users')
        order_obj = request.registry.get('sale.order')

        partner_lang = request.lang if request.lang in [lang.code for lang in request.website.language_ids] else None


        billing_info = {'customer': True}
        if partner_lang:
            billing_info['lang'] = partner_lang
        billing_info.update(self.checkout_parse('billing', checkout, True))

        # set partner_id
        partner_id = None
        if request.uid != request.website.user_id.id:
            partner_id = orm_user.browse(cr, SUPERUSER_ID, uid, context=context).partner_id.id
            _logger.debug("SAVE: PARTNER_ID CONTEXT: " + str(partner_id))


        elif order.partner_id:
            _logger.debug("SAVE: PARTNER_ID ORDER: " + str(order.partner_id))

            user_ids = request.registry['res.users'].search(cr, SUPERUSER_ID,
                [("partner_id", "=", order.partner_id.id)], context=dict(context or {}, active_test=False))
            if not user_ids or request.website.user_id.id not in user_ids:
                partner_id = order.partner_id.id


        if partner_id and request.website.partner_id.id != partner_id:

            _logger.debug("UPDATE RES.PARTNER: " +str(billing_info))

            orm_partner.write(cr, SUPERUSER_ID, [partner_id], billing_info, context=context)
        else:
            # create partner
            partner_id = orm_partner.create(cr, SUPERUSER_ID, billing_info, context=context)

        # create a new shipping partner
        if checkout.get('shipping_id') == -1:
            _logger.debug("PARTNER_ID ===== SHIPPING_ID ")

            shipping_info = self._get_shipping_info(checkout)
            if partner_lang:
                shipping_info['lang'] = partner_lang
            shipping_info['parent_id'] = partner_id
            checkout['shipping_id'] = orm_partner.create(cr, SUPERUSER_ID, shipping_info, context)

        # Update shipping info. Si es distinto al partner.
        elif partner_id != checkout.get('shipping_id'):

            shipping_info = self._get_shipping_info(checkout)

            if partner_lang:
                shipping_info['lang'] = partner_lang
            shipping_info['parent_id'] = partner_id


            _logger.debug("SHIPPING_ID PARENT: " + str(partner_id))
            _logger.debug("SHIPPING_ID: " + str(checkout.get('shipping_id')) + " SHIPPING_INFO: " + str(shipping_info))
            orm_partner.write(cr, SUPERUSER_ID, checkout.get('shipping_id'), shipping_info, context)




        order_info = {
            'partner_id': partner_id,
            'message_follower_ids': [(4, partner_id), (3, request.website.partner_id.id)],
            'partner_invoice_id': partner_id,
            'partner_shipping_id': checkout.get('shipping_id'),
            'note': checkout.get('note'),

        }
        #order_info.update(order_obj.onchange_partner_id(cr, SUPERUSER_ID, [], partner_id, context=context)['value'])
        address_change = order_obj.onchange_delivery_id(cr, SUPERUSER_ID, [], order.company_id.id, partner_id,
                                                        checkout.get('shipping_id'), None, context=context)['value']
        order_info.update(address_change)
        if address_change.get('fiscal_position'):
            fiscal_update = order_obj.onchange_fiscal_position(cr, SUPERUSER_ID, [], address_change['fiscal_position'],
                                                               [(4, l.id) for l in order.order_line], context=None)['value']
            order_info.update(fiscal_update)

        #order_info.pop('user_id')



        #_logger.debug("SHIPPING_ID" + str(checkout.get('shipping_id')))

        order_info.update(partner_shipping_id=checkout.get('shipping_id') or partner_id)
        #_logger.debug("ORDER INFO: " + str(order_info))

        order_obj.write(cr, SUPERUSER_ID, [order.id], order_info, context=context)


    def _get_shipping_info(self, checkout):
        shipping_info = {}
        shipping_info.update(self.checkout_parse('shipping', checkout, True))
        shipping_info['type'] = 'delivery'

        if 'street_type' in shipping_info and shipping_info['street_type']:
            shipping_info['street_type'] = shipping_info['street_type']

        return shipping_info


    # Actualizar los datos del street_type
    def checkout_parse(self, address_type, data, remove_prefix=False):
        values = super(cs_website_sale, self).checkout_parse(address_type, data, remove_prefix)
        if values.get('street_type'):
            values['street_type'] = int(values['street_type'])
        return values


    def checkout_values(self, data=None):
        #_logger.debug("CHECKOUT_VALUES: "+ str(data))

        values = super(cs_website_sale, self).checkout_values(data)

        cr, uid, context, registry = request.cr, request.uid, request.context, request.registry

        obj_street_types = registry.get('res.partner.street_type')
        ids = obj_street_types.search(cr, SUPERUSER_ID, [], context=context)
        street_types = obj_street_types.browse(cr, SUPERUSER_ID, ids, context)

        values.update({'street_types':street_types})

        if data:

            checkout = values["checkout"]
            # Pais. Añadir ES al vat cuando es España y si no lo han puesto.
            country_id = checkout["country_id"]
            if country_id:
                vat = checkout["vat"]
                #_logger.debug("PASO1: VAT:"+ str(vat) + " COUNTRY_ID" + str(country_id))
                obj=request.registry.get('res.country')
                ids = obj.search(cr, SUPERUSER_ID, [('id', '=', country_id)], context=context)
                if ids:
                    country_id = obj.browse(cr,SUPERUSER_ID,ids[0])

                    #_logger.debug("PASO2: COUNTRY_ID.CODE" + str(country_id.code))
                    if vat[:2] != country_id.code:
                        checkout['vat'] = country_id.code + vat



            street_type = None
            if 'street_type' in data and data['street_type']:
                obj = registry.get('res.partner.street_type')
                ids = obj.search(cr, SUPERUSER_ID, [('id','=',data['street_type'])], context=context)
                if ids:
                    street_type = obj.browse(cr, SUPERUSER_ID, ids[0], context)



            name1 = data.get("name1")
            name2 = data.get("name2")
            street_name = data.get("street_name")
            street_number = data.get("street_number")
            street_esc = data.get("street_esc")
            street_piso = data.get("street_piso")
            street_puerta = data.get("street_puerta")


            name = "%s, %s" % (name2 or "" ,name1 or "")
            street = "%s %s %s" % ((street_type and street_type.name) or '', street_name or "", street_number or "")
            street += " %s" % street_esc or ""
            street += " %s" % street_piso or ""
            street += " %s" % street_puerta or ""

            #_logger.debug("LAST STREET_TYPE: " + str(street_type))

            values['checkout'].update({
                'name' : name,
                'street2' : street,
                'street_type_id' : street_type and street_type.id or None,
                'street_esc' : street_esc,
                'street_piso' : street_piso,
                'street_puerta' : street_puerta,
            })

            # Comprobar si la dirección de envío es distinta a la dirección de facturación
            shipping_id = None
            if 'shipping_id' in values['checkout']:
                shipping_id = int(data["shipping_id"])

            if shipping_id:
                shipping_street_type = None
                if 'shipping_street_type' in data and data['shipping_street_type']:
                    obj = registry.get('res.partner.street_type')
                    ids = obj.search(cr, SUPERUSER_ID, [('id','=',data['shipping_street_type'])], context=context)
                    if ids:
                        shipping_street_type = obj.browse(cr, SUPERUSER_ID, ids[0], context)



                #_logger.debug("SHIPPING_STREET_TYPE: " + str(shipping_street_type))

                shipping_street_name = data.get("shipping_street_name")
                shipping_street_number = data.get("shipping_street_number")
                shipping_street_esc = data.get("shipping_street_esc")
                shipping_street_piso = data.get("shipping_street_piso")
                shipping_street_puerta = data.get("shipping_street_puerta")

                shipping_street = "%s %s %s" % ((shipping_street_type and shipping_street_type.name) or '', shipping_street_name or "", shipping_street_number or "")
                shipping_street += " %s" % shipping_street_esc or ""
                shipping_street += " %s" % shipping_street_piso or ""
                shipping_street += " %s" % shipping_street_puerta or ""

                #_logger.debug("SHIPPING_STREET_TYPE: " + str(shipping_street))

                values['checkout'].update({
                    'shipping_name' : values['checkout'].get('name'),
                    'shipping_phone' : values['checkout'].get('phone'),

                    'shipping_street' : shipping_street,
                    'shipping_street_type_id' : shipping_street_type and shipping_street_type.id,
                    'shipping_street_esc' : shipping_street_esc,
                    'shipping_street_piso' : shipping_street_piso,
                    'shipping_street_puerta' : shipping_street_puerta,
                })

            # Recuperar las obaservaciones del formulario.
            if data and 'note' in data:
                note = data['note']

                values['checkout'].update({
                    'note':note,
                    })
        else:
            if 'street_type' in values['checkout']:
                values['checkout'].update({
                    'street_type_id' : values['checkout'].get('street_type'),
                })

            if 'shipping_street_type' in values['checkout']:
                values['checkout'].update({
                    'shipping_street_type_id' : values['checkout'].get('shipping_street_type'),
                })

        # Bloquear la localización.
        values['zip_code_lock'] = True

        return values


    def checkout_form_validate(self, order, data):
        #_logger.debug("CHECKOUT_FORM_VALIDATE: "+ str(data))
        error = super(cs_website_sale, self).checkout_form_validate(data)

        fzip = "zip"

        zip_code = data.get(fzip, '')
        if "shipping_zip" in data:
            fzip = "shipping_zip"
            zip_code = data.get(fzip)

        zip_code = '{:05.0f}'.format(int(zip_code))

        code = 'P'
        if zip_code[:2] in ['35','38']:
            code = 'C'
        if zip_code[:2] in ['07']:
            code = 'B'

        if order.pricelist_id.code != code:
            #_logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            #_logger.debug("La tarifa seleccionada no corresponde al destino especificado.")
            #_logger.debug("CHECK_PRICELIST: ZIP %s:%s" % (fzip, zip_code) )
            #_logger.debug("CHECK_PRICELIST: PRICELIST: %s(%s)" % (order.pricelist_id.name, order.pricelist_id.code))
            #_logger.debug("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            error['pricelist'] = 'error'
            error[fzip] = 'error'

        return error


    # Sobreescribir el tratamiento del pago.
    @http.route(['/shop/payment/transaction/<int:acquirer_id>'], type='json', auth="public", website=True)
    def payment_transaction(self, acquirer_id):

        #_logger.debug("**** PAYMENT_TRANSACTION")
        """ Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button. After having
        created the transaction, the event continues and the user is redirected
        to the acquirer website.

        :param int acquirer_id: id of a payment.acquirer record. If not set the
                                user is redirected to the checkout page
        """
        cr, uid, context = request.cr, request.uid, request.context
        payment_obj = request.registry.get('payment.acquirer')
        transaction_obj = request.registry.get('payment.transaction')
        order = request.website.sale_get_order(context=context)

        if not order or not order.order_line or acquirer_id is None:
            return request.redirect("/shop/checkout")

        assert order.partner_id.id != request.website.partner_id.id

        payment_amount = order.payment_amount
        if payment_amount == 0:
            payment_amount = order.amount_total

        #_logger.debug("PAYMENT_TRANSACTION: IMPORTE DEL PAGO: "+  str(payment_amount))


        # find an already existing transaction
        tx = request.website.sale_get_transaction()
        if tx:
            tx_id = tx.id
            if tx.sale_order_id.id != order.id or tx.state in ['error', 'cancel'] or tx.acquirer_id.id != acquirer_id:
                tx = False
                tx_id = False
            elif tx.state == 'draft':  # button cliked but no more info -> rewrite on tx or create a new one ?
                tx.write(dict(transaction_obj.on_change_partner_id(cr, SUPERUSER_ID, None, order.partner_id.id,
                context=context).get('values', {}), amount=payment_amount))
        if not tx:
            tx_id = transaction_obj.create(cr, SUPERUSER_ID, {
                'acquirer_id': acquirer_id,
                'type': 'form',
                'amount': payment_amount,
                'currency_id': order.pricelist_id.currency_id.id,
                'partner_id': order.partner_id.id,
                'partner_country_id': order.partner_id.country_id.id,
                'reference': request.env['payment.transaction'].get_next_reference(order.name),
                'sale_order_id': order.id,
            }, context=context)
            request.session['sale_transaction_id'] = tx_id
            tx = transaction_obj.browse(cr, SUPERUSER_ID, tx_id, context=context)

        # update quotation
        request.registry['sale.order'].write(
            cr, SUPERUSER_ID, [order.id], {
                'payment_acquirer_id': acquirer_id,
                'payment_tx_id': request.session['sale_transaction_id']
            }, context=context)

        return payment_obj.render(
            cr, SUPERUSER_ID, tx.acquirer_id.id,
            tx.reference,
            payment_amount,
            order.pricelist_id.currency_id.id,
            partner_id=order.partner_shipping_id.id or order.partner_invoice_id.id,
            tx_values={
                'return_url': '/shop/payment/validate',
            },
            context=dict(context, submit_class='btn btn-primary', submit_txt=_('Pay Now')))



    @http.route(['/shop/payment/partial'], type='json', auth="public", website=True)
    def payment_partial(self, set_partial_payment, **kw):
        cr, uid, context = request.cr, request.uid, request.context

        #_logger.debug("**** PAYMENT_PARTIAL")
        order = request.website.sale_get_order(context=context)

        if not order or not order.order_line:
            return request.redirect("/shop/checkout")

        assert order.partner_id.id != request.website.partner_id.id



        payment_amount = order.amount_total
        if set_partial_payment:
            percentage = 40.0 / 100
            payment_amount = round(order.amount_total * percentage,2)

        # Guardar el valor en el pedido.
        order.payment_amount = payment_amount



        values = {
            'zip_code_lock' : True,
            'payment_amount' : payment_amount,
            'pending_payment' : round(order.amount_total-payment_amount,2),
        }

        #_logger.debug(str(values))

        return values



    @http.route(['/shop/confirmation'], type='http', auth="public", website=True)
    def payment_confirmation(self, **post):
        r = super(cs_website_sale, self).payment_confirmation(**post)

        # No permitir cambiar la localización
        r.qcontext['zip_code_lock'] = True


        return r

    @http.route(['/shop/cart/add'], type='http', auth="public", methods=['GET'], website=True)
    def cart_add_product(self, product_id, add_qty=1, set_qty=0, **kw):
        r = super(cs_website_sale, self).cart_update(product_id,add_qty,set_qty, **kw)
        return request.redirect("/shop/cart")



    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True)
    def cart_update_json(self, product_id, line_id, add_qty=None, set_qty=None, display=True):
        order = request.website.sale_get_order(force_create=1)
        if order.state != 'draft':
            request.website.sale_reset()
            return {}

        if not order.cart_quantity:
            request.website.sale_reset()
            return {}
        if not display:
            return None

        pricelist_id = request.session.get("pricelist")
        #_logger.debug("UPDATE_JSON: PRICELIST_ID " + str(pricelist_id))

        value = order._cart_update(product_id=product_id, line_id=line_id, add_qty=add_qty, set_qty=set_qty)

        #_logger.debug("UPDATE_JSON: " + "+++++++++++++++++++++++++++++++++++++++++++++++++++++")
        #_logger.debug("UPDATE_JSON: ORDER.AMOUNT_TOTAL: " + str(order.amount_total))

        value['cart_quantity'] = order.cart_quantity
        value['website_sale.total'] = request.website._render("website_sale.total", {
                'website_sale_order': request.website.sale_get_order()
            })
        return value

    # Permite elegir por parte del usuario la forma de ver los productos.
    @http.route(['/shop/grid'], type='json', auth="public", methods=['POST'], website=True)
    def products_grid(self, grid):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        # set True for reload window.
        res = {'reload' : False}

        product_grid = request.session.get("product_grid", True)
        if product_grid != grid:
            res['reload'] = True
            request.session["product_grid"] =  grid

        #_logger.debug("GRID: " + str(product_grid))
        #_logger.debug("RES: " + str(res))

        return res

    # Indicar el tipo de filtro a aplicar en las próximas consultas.
    @http.route(['/shop/filter'], type='json', auth="public", methods=['POST'], website=True)
    def filter(self, filter_type, value):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        res = {'reload' : False}
        filters = request.session.get("filters", {})
        if filter_type in filters:
            filter = filters[filter_type]
            if not filter['value'] or filter['value']!=value:
                filters[filter_type]['value'] = int(value)

                # Si el valor coincide con el máximo, reseteo el filtro.
                if int(filters[filter_type]['value']) == int(filters[filter_type]['max']):
                    filters[filter_type]['value'] = False

                request.session['filters'] = filters
                res['reload'] = True

        _logger.debug("New filters :" + str(request.session['filters']))
        return res

class cs_website(openerp.addons.website.controllers.main.Website):

    # Añade al response todo lo necesario para poder hacer una búsqueda global.
    def _global_search(self, r, search=''):
        keep = QueryURL1('/shop', search=search)
        r.qcontext['category'] = False
        r.qcontext['keep'] = keep
        r.qcontext['get_attribute_value_ids'] = self.get_attribute_value_ids
        r.qcontext['get_pack_attribute_value_ids'] = self.get_pack_attribute_value_ids

        if 'zip_code_state' in request.session:
            r.qcontext['zip_code'] = request.session['zip_code']
            r.qcontext['zip_code_state'] = request.session['zip_code_state']

        return r

    def get_attribute_value_ids(self, product):
        return get_attribute_value_ids1(product)

    def get_pack_attribute_value_ids(self, product):
        return get_attribute_value_ids_promo_packs(product)

    # Preparar la búsqueda global.
    @http.route('/', type='http', auth="public", website=True)
    def index(self, search='', ** kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        r = self._global_search(super(cs_website, self).index( ** kw), search)


        #Cargar los atributos por defecto de todas las categorías públicas.
        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)
        attrib_set = []
        for c in categs:
            if c.attribute_default_value:
                attrib_set += [c.attribute_default_value.id]

        r.qcontext['attrib_set'] = set(attrib_set)

        if 'zip_code_state' in request.session:
            r.qcontext['zip_code'] = request.session['zip_code']
            r.qcontext['zip_code_state'] = request.session['zip_code_state']

        # Obtener la campaña activa.
        Offer = pool['product.offer']
        r.qcontext['offer'] = Offer.get_first_offer(cr, uid, context)

        return r

    # Preparar la búsqueda global.
    @http.route('/page/<page:page>', type='http', auth="public", website=True)
    def page(self, page, search='', ** opt):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry
        r = self._global_search(super(cs_website, self).page(page, ** opt), search)

        # Añadir attrib_set para poder ver las medidas en los carousels de productos.
        attrib_set = request.session.get("attrib_set",False)

        #Cargar los atributos por defecto de todas las categorías públicas.
        category_obj = pool['product.public.category']
        category_ids = category_obj.search(cr, uid, [('parent_id', '=', False)], context=context)
        categs = category_obj.browse(cr, uid, category_ids, context=context)

        # Inicializar la medida seleccionada anteriormente.
        if not attrib_set:
            attrib_set = []
            for c in categs:
                if c.attribute_default_value:
                    attrib_set += [c.attribute_default_value.id]

        r.qcontext['attrib_set'] = set(attrib_set)

        if 'zip_code_state' in request.session:
            r.qcontext['zip_code'] = request.session['zip_code']
            r.qcontext['zip_code_state'] = request.session['zip_code_state']

        # Obtener la campaña activa.
        Offer = pool['product.offer']
        r.qcontext['offer'] = Offer.get_first_offer(cr, uid, context)

        return r


    @http.route(['/shop/copy'], type='json', auth="public", methods=['POST'], website=True)
    def tools_copy(self, clipboard, ** kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry


        request.session['clipboard'] = clipboard
        #_logger.debug("Clipboard copy:" + str(clipboard))
        values = {}
        return values

    @http.route(['/shop/paste'], type='json', auth="public", methods=['POST'], website=True)
    def tools_paste(self, ** kw):
        cr, uid, context, pool = request.cr, request.uid, request.context, request.registry

        clipboard = request.session['clipboard'] if 'clipboard' in request.session else ''

        #   _logger.debug("Clipboard paste:" + str(clipboard))
        values = {
            'clipboard': clipboard,
        }
        return values
