# -*- coding: utf-8 -*-
from openerp import api, tools
from openerp.osv import osv, fields, expression
import openerp.addons.decimal_precision as dp
import hashlib
from openerp.tools import html_escape as escape, ustr, image_resize_and_sharpen, image_save_for_web
import cStringIO
from PIL import Image
from PIL import ImageFile

import base64
import logging
_logger = logging.getLogger(__name__)
from openerp import SUPERUSER_ID


from cs_tools import *
import re

from openerp.http import Controller, route, request

class product_brand(osv.osv):
    _name = 'product.brand'
    _description = 'Brand of product'
    _order = "sequence, name"
    _inherit = ['website.seo.metadata']

    """
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _brand_set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
    """

    def _get_summary(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.website_short_description:
                result[obj.id] = obj.website_short_description
            else:
                text = html2text(obj.website_description)
                text = extract_paragraphs_from_text(text, 3, 350)
                result[obj.id] = text+'.'
        return result

    def image_url(self, cr, uid, record, field, size=None, context=None):
        """Returns a local url that points to the image field of a given browse record."""
        model = record._name
        sudo_record = record.sudo()
        id = '%s_%s' % (record.id, hashlib.sha1(sudo_record.write_date or sudo_record.create_date or '').hexdigest()[0:7])
        size = '' if size is None else '/%s' % size
        return '/website/image/%s/%s/%s%s' % (model, id, field, size)



    """
    'image_medium': fields.function(_get_image, fnct_inv=_brand_set_image,
        string="Medium-sized image", type="binary", multi="_get_image",
        store={
            'product.brand': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
        },
        help="Medium-sized image of the category. It is automatically "\
             "resized as a 128x128px image, with aspect ratio preserved. "\
             "Use this field in form views or some kanban views."),
    'image_small': fields.function(_get_image, fnct_inv=_brand_set_image,
        string="Smal-sized image", type="binary", multi="_get_image",
        store={
            'product.brand': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
        },
        help="Small-sized image of the category. It is automatically "\
             "resized as a 64x64px image, with aspect ratio preserved. "\
             "Use this field anywhere a small image is required."),
    """

    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'sequence': fields.integer('Sequence', help="Determine the display order"),
        'delivery_message': fields.char('Mensaje de entrega', default='de 5 a 8 días laborales.', translate=True),

        'image': fields.binary("Image",
            help="This field holds the image used as image for the category, limited to 1024x1024px."),
        'image_medium': fields.binary("Image",
            help="This field holds the image used as image for the category, limited to 1024x1024px."),
        'transparent_image': fields.binary("Imagen transparente",),



        # Datos específicos para la web.
        'website_description': fields.html('Website description', translate=True),
        'website_short_description': fields.html('Descripción corta', translate=True),
        'website_summary': fields.function(_get_summary , type="html", string='Summary'),
    }

    _defaults = {
        'sequence': 1,
    }


class product_template(osv.osv):
    _inherit = "product.template"


    def _optimize(self, data):

        ImageFile.LOAD_TRUNCATED_IMAGES = True


        image = data['image'].decode('base64')
        image = Image.open(cStringIO.StringIO(image))

        size = (1024,1024)
        img = image_resize_and_sharpen(image, size, preserve_aspect_ratio=True)
        img = image_save_for_web(img,format=image.format)

        return base64.encodestring(img)


    # Permite optimizar la importación de imágenes.
    def write_img_optimize(self, cr, uid, ids, data, context=None):
        if data['image']:
            data['image'] = self._optimize(data)
        return super(product_template, self).write(cr, uid, ids, data, context=context)


    # Devolver las url's de las imágenes de un producto.
    def _get_image_url(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)

        for obj in self.browse(cr, uid, ids, context=context):

            slide = 0

            #main product.image
            hashid = '%s_%s' % (obj.id, hashlib.sha1(obj.write_date or obj.create_date or '').hexdigest()[0:7])
            imgs = [{
                'url':'/website/image/product.template/%s/image' % hashid,
                'slide' : slide,
            }]

            slide += 1
            # Imágenes principales del producto
            att_obj = self.pool.get('ir.attachment')
            att_ids = att_obj.search(cr, uid, [('res_model','=','product.template'),('res_id','=',obj.id)], order='sequence,id', context=context)
            atts = att_obj.browse(cr, uid, att_ids, context=context)
            for img in atts:
                hashid = '%s_%s' % (img.id, hashlib.sha1(img.write_date or img.create_date or '').hexdigest()[0:7])
                imgs.append({
                    'url': '/website/image/ir.attachment/%s/datas' % hashid,
                    'slide' : slide,
                })
                slide += 1

            # Imágenes en función de los atributos.
            ProductAttributeImage = self.pool.get('product.attribute.image')
            ids = ProductAttributeImage.search(cr, uid, [('product_tmpl_id','=',obj.id)], context=context)
            images = ProductAttributeImage.browse(cr, uid, ids, context=context)
            for img in images:
                hashid = '%s_%s' % (img.id, hashlib.sha1(img.write_date or img.create_date or '').hexdigest()[0:7])
                imgs.append({
                    'url': '/website/image/product.attribute.image/%s/image' % hashid,
                    'slide' : slide,
                    'value' : img.value_id.id,
                })
                slide += 1

            result[obj.id] = imgs
        return result

    def _get_summary(self, cr, uid, ids, name, args, context=None):

        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.website_short_description:
                result[obj.id] = obj.website_short_description
            else:
                text = html2text(obj.website_benefits)
                text = extract_paragraphs_from_text(text, 3, 350)
                result[obj.id] = text+'.'
        return result

    def _get_short_name(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = ' '.join(obj.name.split(' ')[0:2])
        return result


    def _get_image_is_set(self, cr, uid, ids, name, args, context=None):

        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image
        return result

    def getLowPrice(self):
        low = self.product_variant_ids and self.product_variant_ids[0].price or 0
        for x in self.product_variant_ids:
            if x.price < low:
                low = x.price
        return low

    def _product_template_price(self, cr, uid, ids, name, arg, context=None):
        result = super(product_template, self)._product_template_price(cr, uid, ids, name, arg, context)

        for obj in self.browse(cr, uid, ids, context=context):
            if obj.product_variant_count == 1:
                result[obj.id] = obj.product_variant_ids[0].price
        return result

    def _product_template_list_price(self, cr, uid, ids, name, arg, context=None):
        result = dict.fromkeys(ids, 0)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.product_variant_count == 1:
                result[obj.id] = obj.product_variant_ids[0].list_price
        return result

    def _product_template_list_discount(self, cr, uid, ids, name, arg, context=None):
        result = dict.fromkeys(ids, 0)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.product_variant_count == 1:
                result[obj.id] = obj.product_variant_ids[0].list_discount
        return result

    def _product_template_list_discount_offer(self, cr, uid, ids, name, arg, context=None):
        result = dict.fromkeys(ids, 0)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.product_variant_count == 1:
                result[obj.id] = obj.product_variant_ids[0].list_discount_offer
        return result




    # Retorna las ofertas activas que tiene un producto.
    # {'CODE':[offer, offer.group,[discounts]   }
    def _get_active_offer(self, cr, uid, ids, codes, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):

            # Localizar los grupos de oferta que tienen el producto.
            r = {}
            for p in obj.product_offer_group_ids:

                #_logger.debug("PRODUCT_OFFER_GROUP: "+ str(p.name))

                # Oferta por grupo de productos:


                # Ofertas con descuentos especiales por grupo.
                for plo in p.product_offer_line_ids:
                    if plo.offer_id.active_now and ((not codes) or (plo.offer_id.code in codes)):
                        r.update({plo.offer_id.code : [ plo.offer_id, [plo.discount1, plo.discount2]] })
            result[obj.id] = r
        return result

    # get all active offers for product.
    def get_active_offers(self, cr, uid, ids, context=None):
        id = ids[0]

        #_logger.debug("PRDUCT_TEMPLATES_IDS:" + str(ids))
        r = self._get_active_offer(cr,SUPERUSER_ID, ids, False, context)
        return r[id]

    # get active offer for code.
    def get_active_offer(self, cr, uid, ids, code, context=None):
        id = ids[0]
        #_logger.debug("PRDUCT_TEMPLATES_IDS:" + str(ids))
        #_logger.debug("CODE:" + str(code))

        r = self._get_active_offer(cr,SUPERUSER_ID,ids,[code],context)
        return r[id]

    # Calcular las offertas activas de un producto.
    def _get_active_product_offer_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for product_id in self.browse(cr, uid, ids, context=context):

            # Localizar todas las ofertas donde está incluído el producto.
            ofs = []
            for og in product_id.product_offer_group_ids:
                ofs+=([offer.id for offer in og.offer_ids if offer.active_now])

            # Añadir las ofertas para todos los productos.
            Offer = self.pool.get('product.offer')
            offer_ids = Offer.search(cr, uid, [('all_products','=',True)], context=context)
            if offer_ids:
                offers = Offer.browse(cr, uid, offer_ids, context=context)

                for offer in offers:
                    if not offer.active_now:
                        continue

                    # comprobar si el producto no es una excepción de la oferta.
                    if not offer.exceptions_product_offer_group_id:
                        # Si no hay excepciones, añado la oferta.
                        ofs+=[offer.id]
                    else:
                        # Si hay excepiones, compruebo que el producto no es una excepción.
                        if not product_id.id in [p.id for p in offer.exceptions_product_offer_group_id.product_tmpl_ids]:
                            ofs+=[offer.id]


            # Quitar los duplicados.
            ofs = list(set(ofs))
            result[product_id.id]=ofs


        return result


    # Devolver la primera clasificación.
    def _first_public_category(self, cr, uid, ids, name, arg, context=None):
        result = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.public_categ_ids:
                result[obj.id] = obj.public_categ_ids[0].name
        return result

    # Devolver la claseficación de productos de google.
    # https://support.google.com/merchants/answer/6324436?visit_id=1-636291684189224120-3275772598&rd=1
    def _google_product_category(self, cr, uid, ids, name, arg, context=None):
        result = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.public_categ_ids:
                result[obj.id] = obj.public_categ_ids[0].google_product_category
        return result


    def _cross_selling_products(self, cr, uid, product_id, context=None):
        return []

    def cross_selling_products(self, cr, uid, ids, field_name, arg, context=None):
        _logger.debug("CROSS_SELLING_FIELD")
        ProductTemplate = self.pool.get('product.template')
        res = {}
        for product_id in self.browse(cr, uid, ids, context=context):
            cross_ids = self._cross_selling_products(cr, uid, product_id, context)
            res[product_id.id] = ProductTemplate.browse(cr, uid, cross_ids, context=context)

        return res


    # Si cambia el default_code, actualizarlo en todas las variantes.
    def write(self, cr, uid, ids, vals, context=None):
        res = super(product_template, self).write(cr, uid, ids, vals, context=context)
        if 'default_code' in vals:
            for product_tmpl_id in self.browse(cr, uid, ids, context=context):
                product_tmpl_id.product_variant_ids.write({'default_code':product_tmpl_id.default_code})

        return res

    def _view_product_online(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = "/shop/product/-%d" % obj.id
        return result


    _columns = {
        'view_product_online': fields.function(_view_product_online,type="char", string='Ver la ficha de producto'),

        'default_code2' : fields.char('Referencia Fabricante', help="Si no está informada, se utilizan la propia referencia interna."),
        'brand_id': fields.many2one('product.brand', 'Product Brand', help='Brand of product'),
        'website_benefits': fields.html('Benefits', translate=True),
        'image_url': fields.function(_get_image_url, type='binary', string='Images', help="Images"),
        'website_summary': fields.function(_get_summary,type="html", string='Summary', translate=True),
        'website_short_description': fields.html('Descripción corta', translate=True),

        'image_is_set': fields.function(_get_image_is_set,type="boolean", string='Imagen establecida'),

        'replace_by': fields.many2one('product.template', 'Reemplazado por', ondelete="restrict", help='Indicar el producto que lo reemplaza'),

        # Product group.
        'product_group_type': fields.selection([(1,'Producto agrupado'),], 'Tipo de agrupación', help='Establecer el tipo de agrupación'),
        'product_group_attribute_id': fields.many2one('product.attribute', 'Atributo de agrupación', ondelete="restrict", help='Indicar el atributo por el que se agrupan los productos.'),
        'product_group_attribute_value_id': fields.many2one('product.attribute.value', 'Valor del atributo de agrupación', help='Indicar el atributo por el que se agrupan los productos.'),
        'product_group_id': fields.many2one('product.template', 'Producto agrupado', domain=[('product_group_type','!=',False)], ondelete="restrict", help='Indicar el producto que agrupado'),
        'product_group_ids': fields.one2many('product.template', 'product_group_id', 'Productos agrupados', help="Indica los productos que forman parte de un grupo"),
        'product_group_images': fields.boolean('Añadir las imágenes', help='Añadir las imágenes de los componentes'),

        # Packs.
        # Lineas del pack
        'product_pack_line_ids': fields.one2many('product.pack.line', 'product_tmpl_id', 'Componentes del pack', copy=False),
        'pack_ids': fields.many2many('product.pack', 'product_pack_line', 'product_tmpl_id', 'pack_id', 'Packs'),

        # cross_selling
        'cross_selling_product_ids': fields.function(cross_selling_products, type="many2many", obj="product.template", string='Cross_selling Products', help="Products to propose when add to cart."),



        'ratingplus': fields.integer('Rating plus',help="Rating plus"),

        # Redefine fields.
        'price': fields.function(_product_template_price, type='float', string='Price', digits_compute=dp.get_precision('Product Price')),
        'list_price': fields.function(_product_template_list_price, type='float', string='Public product list price', help="Public product list price", digits_compute=dp.get_precision('Product Price')),
        'list_discount': fields.function(_product_template_list_discount, type='float', string='Public product discount', help="Public product discount",
                digits_compute=dp.get_precision('Product discount') or 0),
        'lst_discount' : fields.related('list_discount', type="float", string='Public discount'),

        'list_discount_offer': fields.function(_product_template_list_discount_offer, type='float', string='Public product discount', help="Public product discount",
                digits_compute=dp.get_precision('Product discount') or 0),
        'lst_discount_offer' : fields.related('list_discount_offer', type="float", string='Public discount offer'),


        # Disponible sólo en tienda física.
        'only_physical_store': fields.boolean('Disponible en tienda física'),
        'only_physical_store_text': fields.char('Texto tienda física', translate=True),
        'website_sale_ok': fields.boolean('Disponible para venta online'),


        # grupos de ofertas
        'active_product_offer_ids': fields.function(_get_active_product_offer_ids, type='many2many', relation="product.offer", string="Ofertas del producto"),
        'product_offer_group_ids': fields.many2many('product.offer.group', 'product_template_product_offer_group_rel', 'product_offer_group_id' ,'product_tmpl_id', string='Grupo de productos'),


        'google_product_category': fields.function(_google_product_category, type='char', string='Google Product Category', help="Clasificación en google shopping",),
        'first_public_category': fields.function(_first_public_category, type='char', string='First Product Public Category', help="Clasificación web",),

        # Última actualización de precios a través del webservice de beds.
        'date_last_update': fields.datetime('Última actualización de precios',),

        'website_short_name': fields.function(_get_short_name,type="char", string='Nombre corto', translate=True),

    }

    _defaults = {
        'only_physical_store' : False,
        'website_sale_ok' : True,
        'product_group_images' : True,
    }


class product_product(osv.osv):
    _inherit = "product.product"

    # Acceder a la lista de precios pública.
    # Retorna una lista de precios sin aplicar el descuento.
    def _product_list_price(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, 0)

        if context is None:
            context = {}

        base_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.list_price', raise_if_not_found=True)
        version_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.ver0', raise_if_not_found=True)



        pricelist = request.session.get("pricelist")

        if not pricelist:
            pricelist = context.get('pricelist', False)

        if pricelist:
            if not (type(pricelist) is int):
                pricelist = int(pricelist)
            version_id = self.pool['product.pricelist.version'].search(cr, uid, [('pricelist_id','=',pricelist)])
            if version_id:
                version_id = version_id[0]


        #_logger.debug("_PRODUCT_PRICELIST_ID: " + str(pricelist))

        ppi_obj = self.pool.get('product.pricelist.item')
        ppi_ids = ppi_obj.search(cr,uid,[('price_version_id','=',version_id),
                                        ('product_id','in',ids)
                                        ],order="date_last_update asc")

        if ppi_ids:
            for item in ppi_obj.browse(cr,uid,ppi_ids):
                result[item.product_id.id] = item.product_price

        return result

    # Obtener el descuento..
    def _product_list_discount(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, 0)

        if context is None:
            context = {}

        base_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.list_price', raise_if_not_found=True)
        version_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.ver0', raise_if_not_found=True)




        pricelist = context.get('pricelist', False)

        if not pricelist:
                pricelist = request.session.get("pricelist")

        if pricelist:
            if not (type(pricelist) is int):
                pricelist = int(pricelist)



            version_id = self.pool['product.pricelist.version'].search(cr, uid, [('pricelist_id','=',pricelist)])
            if version_id:
                version_id = version_id[0]


        ppi_obj = self.pool.get('product.pricelist.item')
        ppi_ids = ppi_obj.search(cr,uid,[('price_version_id','=',version_id),
                                        ('product_id','in',ids)
                                        ],order="date_last_update asc")

        if ppi_ids:
            for item in ppi_obj.browse(cr,uid,ppi_ids):
                result[item.product_id.id] = item.product_discount

                # Comprobar si hay ofertas activas.
                # Plan renove.
                """
                active_offers = item.product_id.product_tmpl_id.get_active_offer('PR')
                if 'PR' in active_offers:
                    result[item.product_id.id] = active_offers['PR'][1][0]
                """


                #_logger.debug("_PRODUCT_LIST_DISCOUNT PRICELIST: " + str(pricelist) )
                #_logger.debug("_PRODUCT_LIST_DISCOUNT DISCOUNT: " + str(result[item.product_id.id]) )



        return result

    # Obtener el descuento en ofertas especiales.
    def _product_list_discount_offer(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, 0)
        for product_id in self.browse(cr, uid, ids, context=context):


            # Comprobar si hay ofertas activas.
            # Plan renove.
            """
            active_offers = product_id.product_tmpl_id.get_active_offer('PR')

            if 'PR' in active_offers:
                result[product_id.id] = active_offers['PR'][1][1]
            """
            #_logger.debug("%s DESCUENTOS2 : %s " %( product_id.name, str(active_offers)))

        return result

    # Retorna la lista de precios con el descuento aplicado.
    def _product_price(self, cr, uid, ids, name, arg, context=None):
        result = dict.fromkeys(ids, 0)

        #_logger.debug("_PRODUCT_PRICE:")
        #_logger.debug("---------------------------------------------------------------")

        if context is None:
            context = {}

        base_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.list_price', raise_if_not_found=True)
        version_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.ver0', raise_if_not_found=True)

        pricelist = context.get('pricelist', False)
        if not pricelist:
            pricelist = request.session.get("pricelist")


        if pricelist:
            if not (type(pricelist) is int):
                pricelist = int(pricelist)
            version_id = self.pool['product.pricelist.version'].search(cr, uid, [('pricelist_id','=',pricelist)])
            if version_id:
                version_id = version_id[0]


        #_logger.debug("PRICELIST: %s, VERSRION_ID: %s " % (str(pricelist),str(version_id) ))


        ppi_obj = self.pool.get('product.pricelist.item')
        ppi_ids = ppi_obj.search(cr,uid,[('price_version_id','=',version_id),
                                        ('product_id','in',ids)
                                        ],order="date_last_update asc")


        if ppi_ids:
            for item in ppi_obj.browse(cr,uid,ppi_ids):

                result[item.product_id.id] = item.product_price * (1 - item.product_discount / 100)

                # Comprobar si hay ofertas activas.
                # Plan renove.
                """
                active_offers = item.product_id.product_tmpl_id.get_active_offer('PR')
                if 'PR' in active_offers:
                    precio = item.product_price * (1 - active_offers['PR'][1][0] / 100)
                    result[item.product_id.id] = precio * (1 - active_offers['PR'][1][1] / 100)
                """


        #_logger.debug("_PRODUCT_PRICE RESULTADO: " + str(result))

        return result


    # Calcular el precio con descuentos.
    def _fnct_get_discounted_price(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, False)
        for product in self.browse(cr, uid, ids, context=context):
            res[product.id] = (product.lst_price * (1.0 - (product.lst_discount or 0.0) / 100.0))
            if product.lst_discount_offer:
                res[product.id] = (res[product.id] * (1.0 - (product.lst_discount_offer) / 100.0))
        return res


    _columns = {
        # Redefine := lst_price - lst_discount or lst_price - active offers.
        'price': fields.function(_product_price, type='float', string='Price', digits_compute=dp.get_precision('Product Price')),

        # Redefine product.product.list_price
        'list_price': fields.function(_product_list_price, type='float', string='Public product price', help="Public product price", digits_compute=dp.get_precision('Product Price')),

        # Create discount field.
        'lst_discount' : fields.related('list_discount', type="float", string='Public discount'),
        'list_discount': fields.function(_product_list_discount, type='float', string='Public product discount', help="Public product discount",
                digits_compute=dp.get_precision('Product discount') or 0),

        'lst_discount_offer' : fields.related('list_discount_offer', type="float", string='Public discount offer'),
        'list_discount_offer': fields.function(_product_list_discount_offer, type='float', string='Public product discount offer', help="Public product discount offer",
                digits_compute=dp.get_precision('Product discount') or 0),

        'discounted_price': fields.function(_fnct_get_discounted_price, string='Discounted price', type='float', digits_compute=dp.get_precision('Product Price')),

        # Productos agrupados
        'product_group_product_id': fields.many2one('product.product', 'Variante', help='Variante de un producto agrupado.'),



    }



class product_public_category(osv.osv):
    _name = 'product.public.category'
    _inherit = ['product.public.category', 'website.seo.metadata']


    def _get_summary(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.website_short_description:
                result[obj.id] = obj.website_short_description
            else:
                text = html2text(obj.website_description)
                text = extract_paragraphs_from_text(text, 3, 350)
                result[obj.id] = text+'.'

        return result

    _columns = {
        'attribute_ids': fields.many2many('product.attribute', 'category_attribute_rel', 'category_id', 'attribute_id', string='Attributes',),
        'attribute_default_value': fields.many2one('product.attribute.value', string='Attribute default value'),

        # Datos necesarios para poder integrar los productos desde el sistema de BED'S
        'niveles': fields.text('Niveles'),

        # Datos específicos para la web.
        'website_description': fields.html('Descripción página web', translate=True),
        'website_short_description': fields.html('Descripción corta', translate=True),
        'website_summary': fields.function(_get_summary,type="html", string='Summary', translate=True),

        #'active': fields.boolean('Active'),


        'google_product_category': fields.char("Google Product Category"),
    }

    _defaults = {
        #'active': True,
    }

# Imágenes por producto y atributo.
class product_attribute_image(osv.osv):
    _name = "product.attribute.image"
    _columns = {
        'product_tmpl_id': fields.many2one('product.template', 'Product Template', required=True, ondelete='cascade'),
        'value_id': fields.many2one('product.attribute.value', 'Product Attribute Value', required=True, ondelete='cascade'),
        'image': fields.binary("Image", help="Imagen para representar el valor."),
    }

class product_attribute(osv.osv):
    _inherit = "product.attribute"
    _order = 'sequence, name'
    _columns = {
        'sequence': fields.integer('Sequence', help="Determine the display order"),
    }

""" Save image for web """
class ir_attachment(osv.osv):
    _inherit = 'ir.attachment'

    def _optimize(self, data):
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        image = data['datas'].decode('base64')
        image = Image.open(cStringIO.StringIO(image))

        size = (1024,1024)
        img = image_resize_and_sharpen(image, size, preserve_aspect_ratio=True)
        img = image_save_for_web(img,format=image.format)

        return base64.encodestring(img)

    # Permite optimizar la importación de imágenes.
    def write_img_optimize(self, cr, uid, ids, data, context=None):
        if data['file_type'] == 'image/jpeg':
            data['datas'] = self._optimize(data)
        return super(ir_attachment, self).write(cr, uid, ids, data, context=context)

    # Permite optimizar la importación de imágenes.
    def create_img_optimize(self, cr, uid, data, context=None):
        if data['file_type'] == 'image/jpeg':
            data['datas'] = self._optimize(data)
        return super(ir_attachment, self).create(cr, uid, data, context)



class product_public_category_brand(osv.osv):
    _name = 'product.public.category.brand'
    _description = 'Public Category by Brand of product'
    _order = "sequence, name"
    _inherit = ['website.seo.metadata']


    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)


    def _get_summary(self, cr, uid, ids, name, args, context=None):

        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            text = html2text(obj.website_description)
            text = extract_paragraphs_from_text(text, 3, 350)
            result[obj.id] = text+'.'
        return result


    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'sequence': fields.integer('Sequence', help="Determine the display order"),

        'image': fields.binary("Image",
            help="This field holds the image used as image for the category, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'product.public.category.brand': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of the category. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized image", type="binary", multi="_get_image",
            store={
                'product.public.category.brand': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the category. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),



        # Public category.
        'public_category': fields.many2one('product.public.category', 'Public Category'),


        # Brand
        'brand': fields.many2one('product.brand', 'Brand'),

        # Datos específicos para la web.
        'website_description': fields.html('Description for the website', translate=True),
        'website_short_description': fields.html('Descripción corta', translate=True),
        'website_summary': fields.function(_get_summary,type="html", string='Summary', translate=True),
    }

    _defaults = {
        'sequence': 1,
    }







class temp_product_product(osv.osv_memory):
    _name = "product.tools"

    def _temp_check_attribute(self, cr, uid, context, attribute_id, attribute_value, product_template_id, product_product_id):
        pro_obj = self.pool.get('product.product')
        pal_obj = self.pool.get('product.attribute.line')
        pal_vals = {
            'product_tmpl_id': product_template_id,
            'attribute_id': attribute_id,
        }

        pal_id = pal_obj.search(cr,uid,[('product_tmpl_id','=',product_template_id),
                            ('attribute_id','=',attribute_id)])

        if not pal_id:
            pal_id = pal_obj.create(cr,uid,pal_vals)


        pav_obj = self.pool.get('product.attribute.value')
        ids = pav_obj.search(cr,uid,[('attribute_id',"=",attribute_id),('name',"=",attribute_value)])
        if not ids:
            pav_id = pav_obj.create(cr,uid,{"attribute_id":attribute_id, "name":attribute_value})
        else:
            pav_id = ids[0]

        # Actualizar la relación de productos por medida.
        if pav_id and product_product_id:
            #pav_obj.write(cr,uid,pav_id, {'product_ids': [(4,product_product_id)]})
            pal_obj.write(cr,uid,pal_id,{'value_ids': [(4,pav_id)]})

        # Update attribute in product.product.
        pro_vals={}
        pro_vals['attribute_value_ids'] = [(4,pav_id)]

        # Update attribute in product.product.
        pro_obj.write(cr,uid,product_product_id, pro_vals)


        # Actualizar el precio.
        """
        if price_extra <> 0:
            pap_obj = self.pool.get('product.attribute.price')
            pap_ids = pap_obj.search(cr,uid, [('product_tmpl_id','=',product_template_id),('value_id','=',pav_id)])
            pap_vals = {'price_extra':price_extra}
            if pap_ids:
                pap_obj.write(cr,uid,pap_ids,pap_vals)
            else:
                pap_vals['product_tmpl_id'] = product_template_id
                pap_vals['value_id'] = pav_id
                pap_obj.create(cr,uid,pap_vals)
        """

        return {
            'pal_id':pal_id
        }




    def _temp_revisar_medidas(self, cr, uid, **kw):
        _logger.debug("REVISAR MEDIDAS")


        obj = self.pool['ir.model.data']
        medidas_id = obj.xmlid_to_res_id(cr, uid, 'cs_model.product_attribute_measures', raise_if_not_found=True)


        obj_product= self.pool.get('product.product')
        obj_pav = self.pool.get('product.attribute.value')


        ids = obj_product.search(cr,uid,[])

        products = obj_product.browse(cr,uid,ids)
        for product in products:
            oldValues = product.attribute_value_ids
            newValues = []
            s =""
            for old in oldValues:
                s += "(%d, %s)" % (old.id,old.name)

                #localizar el priver valor que exista para el nombre
                id = obj_pav.search(cr,uid,[('attribute_id','=',old.attribute_id.id),('name','=',old.name)],limit=1)
                if id:
                    new = obj_pav.browse(cr,uid,id)
                    newValues.append(new)

            _logger.debug("OLD_VALUES: " + s)

            newValues = list(set(newValues))

            if len(newValues)>0:

                #product.attribute_value_ids = [(5)]
                t =""
                for v in newValues:
                    t += "(%d, %s)" % (v.id,v.name)
                    product.attribute_value_ids = [(4,v.id)]

                _logger.debug("NEW_VALUES: " + t)


    def _temp_ordenar_medidas(self, cr, uid, **kw):
        _logger.debug("ORDENAR MEDIDAS")


        obj = self.pool.get('product.attribute.value')
        ids = obj.search(cr,uid,[])
        pavs = obj.browse(cr,uid,ids)

        alist = [pav for pav in pavs]

        alist.sort(key=self.natural_keys)


        max = 0
        for x in alist:
            if x.sequence > max:
                max = x.sequence


        n =  1
        for x in alist:
            x.sequence = n
            n += 1
            _logger.debug("VALUE: %s" % x.name )





    def atoi(self, text):
        return int(text) if text.isdigit() else text

    def natural_keys(self, pav):

        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        '''
        return [ self.atoi(c) for c in re.split('(\d+)', pav.attribute_id.name + " " + pav.name.strip()) ]
