# -*- coding: utf-8 -*-
from openerp import api, tools
from openerp.osv import osv, fields, expression
import openerp.addons.decimal_precision as dp
import hashlib
from openerp.tools import html_escape as escape, ustr, image_resize_and_sharpen, image_save_for_web
import cStringIO
from PIL import Image
from PIL import ImageFile
from datetime import datetime, timedelta

import base64
import logging
_logger = logging.getLogger(__name__)
from openerp import SUPERUSER_ID


from cs_tools import *
import re

from openerp.http import Controller, route, request

class product_pack(osv.osv):
    _name = 'product.pack'
    _description = "Pack's de productos"
    _order = "sequence, name"
    _inherit = ['website.seo.metadata']

    def _pack_get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _pack_set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)


    def _get_summary(self, cr, uid, ids, name, args, context=None):

        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            if obj.website_short_description:
                result[obj.id] = obj.website_short_description
            else:
                text = html2text(obj.website_description)
                text = extract_paragraphs_from_text(text, 3, 350)
                result[obj.id] = text
        return result

    def image_url(self, cr, uid, record, field, size=None, context=None):
        """Returns a local url that points to the image field of a given browse record."""
        model = record._name
        sudo_record = record.sudo()
        id = '%s_%s' % (record.id, hashlib.sha1(sudo_record.write_date or sudo_record.create_date or '').hexdigest()[0:7])
        size = '' if size is None else '/%s' % size
        return '/website/image/%s/%s/%s%s' % (model, id, field, size)


    def _product_pack_price(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, 0)
        return result

    def _product_pack_list_price(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, 0)
        return result


    def _get_product_tmpl_ids(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        product_obj = self.pool.get('product.template')
        product_pack_line_obj = self.pool.get('product.pack.line')

        for pack_id in ids:
            line_ids = product_pack_line_obj.search(cr, uid, [('pack_id', '=', pack_id)], context=context)
            line_ids = product_pack_line_obj.browse(cr, uid, line_ids, context=context)
            product_ids = list(set([x.product_tmpl_id.id for x in line_ids]))
            res[pack_id] = product_obj.search(cr, uid, [('id', 'in', product_ids)], context=context)
        return res

    @api.depends('active', 'datetime_start', 'datetime_end')
    def _active_now(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            ahora = datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if obj.active and (obj.datetime_start and obj.datetime_start <= ahora) \
                and (obj.datetime_end and obj.datetime_end >= ahora):
                result[obj.id] = True

        return result

    _columns = {
        'name': fields.char('Nombre', required=True, translate=True),
        'subtitle': fields.char('Subtítulo', translate=True),

        'datetime_start': fields.datetime('Inicio', help="Fecha inicial de activación del pack"),
        'datetime_end': fields.datetime('Fin', help="Fecha final de activación del pack"),
        'active': fields.boolean('Activo', help="Permite archivar configuraciones"),
        'active_now': fields.function(_active_now, string="Está activo ahora", type="boolean", ),

        'sequence': fields.integer('Sequence', help="Determina el orden en el que se muestran los packs"),

        'image': fields.binary("Image",
            help="This field holds the image used as image for the category, limited to 1024x1024px."),
        'image_medium': fields.function(_pack_get_image, fnct_inv=_pack_set_image,
            string="Medium-sized image", type="binary", multi="_pack_get_image",
            store={
                'product.brand': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of the category. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_pack_get_image, fnct_inv=_pack_set_image,
            string="Smal-sized image", type="binary", multi="_pack_get_image",
            store={
                'product.brand': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the category. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),

        # Datos específicos para la web.
        'website_description': fields.html('Descripción web', translate=True),
        'website_short_description': fields.html('Descripción corta', translate=True),
        'website_summary': fields.function(_get_summary,type="html", string='Resumen', translate=True),

        # Lineas del pack
        'line_ids': fields.one2many('product.pack.line', 'pack_id', 'Composición', copy=True),

        # Productos del pack.
        'product_tmpl_ids': fields.function(_get_product_tmpl_ids, type='one2many', relation='product.template', string='Productos'),

        'offer_id': fields.many2one('product.offer', 'Oferta', ondelete='set null'),

        # No se utiliza, ya que depende de los atributos (js). pero se necesita para inicializar los campos.
        'price': fields.function(_product_pack_price, type='float', string='Precio', digits_compute=dp.get_precision('Product Price')),
        'list_price': fields.function(_product_pack_list_price, type='float', string='Precio', digits_compute=dp.get_precision('Product Price')),

        # Sale
        'only_physical_store': fields.boolean('Disponible sólo en tienda física'),
        'only_physical_store_text': fields.char('Texto tienda física', translate=True),

    }

    _defaults = {
        'sequence': 10,
    }


class product_pack_line(osv.osv):
    _name = 'product.pack.line'
    _description = 'Componentes del pack'
    _columns = {
        'pack_id': fields.many2one('product.pack', 'Pack', required=True, ondelete='cascade', select=True, readonly=True,),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'product_tmpl_id': fields.many2one('product.template', 'Producto', required=True, ondelete='restrict'),
        'qty': fields.integer('Cantidad'),
    }
    _order = 'pack_id, sequence, id'
    _defaults = {
        'qty': 1,
        'sequence': 10,
    }

"""
Define la configuración de los packs.
"""
class product_pack_config(osv.osv):
    _name = "product.pack.config"
    _description = "Configuración de los packs"
    _order = 'sequence'


    @api.depends('active', 'datetime_start', 'datetime_end')
    def _active_now(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            ahora = datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if obj.active and (obj.datetime_start and obj.datetime_start <= ahora) and (obj.datetime_end and obj.datetime_end >= ahora) :
                result[obj.id] = True

        return result

    _columns = {
        'name': fields.char('Name', required=True, translate=True),

        'sequence': fields.integer('Sequence'),

        'datetime_start': fields.datetime('Inicio', help="Fecha inicial para configuración activa."),
        'datetime_end': fields.datetime('Fin', help="Fecha final para la configuración activa."),
        'active': fields.boolean('Activo', help="Permite archivar configuraciones"),
        'active_now': fields.function(_active_now, string="Está activo ahora", type="boolean", ),
        'color_text': fields.char('Color texto', help="Color asociado a los textos de la oferta"),
        'color_background': fields.char('Color fondo', help="Color asociado al fondo"),
        'image_header_id': fields.binary('Imagen de cabecera', attachment=True, help="Imagen de cabecera para la página de packs."),
        'en_image_header_id': fields.binary('Image of header', attachment=True, help="Image of header for first pack."),

    }
    _defaults = {
        'active': lambda *a: False,
        'sequence': lambda *s: 10,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        # set active False to prevent overlapping active campaign
        # versions
        if not default:
            default = {}
        default['active'] = False
        return super(product_pack_config, self).copy(cr, uid, id, default, context=context)
