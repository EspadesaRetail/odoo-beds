# -*- coding: utf-8 -*-
import openerp
from openerp import tools, api
from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta
from openerp import SUPERUSER_ID

import logging
_logger = logging.getLogger(__name__)



"""
    Devuelve los productos asociados a un grupo de productos y los de todos sus hijos.
    return:  [products]
    """

# Permite definir los distintos tipos de oferta que se producen.
class product_offer(osv.osv):
    _name = "product.offer"
    _description = "Oferta"
    _order = "sequence, name"



    def getOffer(self, cr, uid, ids, context=None):
        result = {}
        for obj in self.browse(cr, openerp.SUPERUSER_ID, ids, context=context):
            if obj.active_now:
                products = obj.product_offer_group_id._get_products_of_group()
                result[obj.id] = {'products':products}

        return result

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    @api.depends('active', 'datetime_start', 'datetime_end')
    def _active_now(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            ahora = datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
            if obj.active and (obj.datetime_start and obj.datetime_start <= ahora) and (obj.datetime_end and obj.datetime_end >= ahora) :
                result[obj.id] = True

        return result

    # Devolver la url de la image de la oferta.
    def _label_url(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            f = 'lang' in context and context['lang'] == 'en_US' and obj.en_image and 'en_image' or 'image'
            result[obj.id] = self.pool.get('website').image_url(cr, uid, obj, f)
        return result

    # Comprueba que no existan dos campañas activas y colisionen en las fechas.
    def _check_datetime(self, cursor, user, ids, context=None):
        for o in self.browse(cursor, user, ids, context=context):
            if not o.active:
                continue

            where = []
            if o.datetime_start:
                where.append("((datetime_end>='%s') or (datetime_end is null))" % (o.datetime_start,))
            if o.datetime_end:
                where.append("((datetime_start<='%s') or (datetime_start is null))" % (o.datetime_end,))

            s = "SELECT id FROM product_offer " \
                    "WHERE "+" and ".join(where) + (where and " and " or "")+ \
                        "active " "AND code = '%s' AND id <> %s" % (o.code, str(o.id))

            _logger.debug("WHERE: " + str(s))

            cursor.execute(s)
            if cursor.fetchall():
                return False

        return True

    # Obtener la primera campaña activa.
    def get_first_offer(self, cr, uid, context=None):
        dt = datetime.now().strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        ids = self.search(cr, SUPERUSER_ID, [('datetime_start', '<=', dt),
            ('datetime_end', '>=', dt)],
            limit=1, context=context)

        if ids:
            return self.browse(cr, uid, ids[0])

        return False


    _columns = {
        'name': fields.char('Name', required=True, translate=True),

        #Condiciones generales
        'code': fields.char('Code', required=True),
        'offer_type': fields.selection([('super','Super oferta'),
                    ('planrenove','Plan renove'),
                    ('default','Condiciones'),
                    ('present','Regalo'),
                    ('siniva','Sin IVA'),
                    ('pack','Pack (Colchón + base de regalo)'),
                    ('pack-dto','Pack + Dto. (En todos los productos)'),
                    ('dto','Descuento adicional'),
                    ], 'Type', copy=False,help='Type'),
        'sequence': fields.integer('Sequence'),

        'image': fields.binary("Imagen",
            help="Imagen utilizada en las ofertas."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Imagen media", type="binary", multi="_get_image",
            store={
                'product.offer': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Imagen tamaño medio utilizada en las ofertas"),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Imagen pequeña", type="binary", multi="_get_image",
            store={
                'product.offer': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Imagen tamaño pequeño utilizada en las ofertas"),

        'en_image': fields.binary("Image", help="Image"),



        # Textos e imagen de las ofertas.
        'website_description_product': fields.html('Mensaje ficha de producto', translate=True, sanitize=False, help="HTML que aparece en la ficha de producto"),
        'website_call_to_action': fields.char('LLamada a la acción', translate=True, help="Texto que aparece en el botó de añadir al carrito"),

        #Condiciones generales
        'all_products': fields.boolean('Aplica a todos los productos'),
        'exceptions_product_offer_group_id': fields.many2one('product.offer.group', 'Excepciones', ondelete='restrict', select=True),

        # Condiciones por grupo de productos.
        'product_offer_group_id': fields.many2one('product.offer.group', 'Grupo de productos', ondelete='restrict', select=True),

        # Condiciones multigrupo
        'product_offer_line_ids': fields.one2many('product.offer.line', 'offer_id', 'Condiciones', copy=True),

        # Condiciones por pack.
        'pack_id': fields.many2one('product.pack', 'Pack', ondelete='restrict'),
        'pack_ids': fields.one2many('product.pack', 'offer_id', 'Packs incluídos'),

        'datetime_start': fields.datetime('Inicio', help="Fecha inicial de la oferta."),
        'datetime_end': fields.datetime('Fin', help="Fecha final de la oferta."),

        # Campañas de regalo.
        'present_id' : fields.many2one('product.product', string="Regalo", select=1, ondelete='cascade', required=False),
        'present_ids': fields.one2many('product.offer.present', 'offer_id', 'Regalos', required=False),

        # Campañas SIN IVA
        'siniva_dto': fields.float('Discount campaña (%)', digits_compute= dp.get_precision('Discount'),),

        # Descuento adicional
        'additional_dto': fields.float('Descuento adicional', digits_compute= dp.get_precision('Discount'),),

        'active': fields.boolean('Active', help="By unchecking the active field you can disable a offer without deleting it."),
        'active_now': fields.function(_active_now, string="Está activa ahora", type="boolean", ),

        'label_url': fields.function(_label_url, type="char",string="Imagen"),


        'color_text': fields.char('Color texto', help="Color asociado a los textos de la oferta"),
        'color_background': fields.char('Color fondo', help="Color asociado al fondo"),
        'image_header_id': fields.binary('Imagen de cabecera', attachment=True, help="Imagen de cabecera definida para la primera oferta."),
        'en_image_header_id': fields.binary('Image header', attachment=True, help="Image of header for first offer."),
    }
    _defaults = {
        'offer_type': lambda *a: 'default',
        'active': lambda *a: False,
        'sequence': lambda *s: 10,
    }

    def copy(self, cr, uid, id, default=None, context=None):
        # set active False to prevent overlapping active campaign
        # versions
        if not default:
            default = {}
        default['active'] = False
        return super(product_offer, self).copy(cr, uid, id, default, context=context)


# Relación de regalos.
class product_offer_present(osv.osv):
    _name = 'product.offer.present'
    _description = 'Regalos'
    _columns = {
        'offer_id': fields.many2one('product.offer', 'Oferta', required=True, ondelete='cascade', select=True, readonly=True,),
        'product_id' : fields.many2one('product.product', 'Producto comprado', select=1, ondelete='cascade', required=True),
        'present_id' : fields.many2one('product.product', 'Regalo', select=1, ondelete='cascade', required=True),
    }
    _order = 'offer_id desc, product_id'


class product_offer_line(osv.osv):

    _name = 'product.offer.line'
    _description = 'Condiciones'
    _columns = {
        'offer_id': fields.many2one('product.offer', 'Oferta', required=True, ondelete='cascade', select=True, readonly=True,),
        #'name': fields.text('Description', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'product_offer_group_id': fields.many2one('product.offer.group', 'Grupo de productos', domain=[('active', '=', True)], change_default=True, ondelete='restrict'),
        'discount1': fields.float('Discount1 (%)', digits_compute= dp.get_precision('Discount'),),
        'discount2': fields.float('Discount2 (%)', digits_compute= dp.get_precision('Discount'),),

        'datetime_start': fields.related('offer_id','datetime_start', type='datetime', relation='product.offer', readonly=True),
        'datetime_end': fields.related('offer_id','datetime_end', type='datetime', relation='product.offer', readonly=True),

        'active': fields.related('offer_id', 'active', type='boolean', relation='product.offer', string='Active', readonly=True),


    }
    _order = 'offer_id desc, sequence, id'
    _defaults = {
        'discount': 0.0,
        'sequence': 10,
    }







class product_offer_group(osv.osv):
    _name = "product.offer.group"
    _description = "Grupos de productos en oferta"
    _order = "sequence, name"

    _constraints = [
        (osv.osv._check_recursion, 'Error ! You cannot create recursive groups.', ['parent_id'])
    ]


    """
    Devuelve los productos asociados a un grupo de productos y los de todos sus hijos.
    return:  [products]
    """
    def _get_products_of_group(self):

        products = []

        group = self
        #_logger.debug("OFFER GROUP: " + str(product_offer_group))

        for product in group.product_tmpl_ids:
            products.append(product)

        if group.child_id:
            for child in group.child_id:
                products += child._get_products_of_group()

        return products



    def name_get(self, cr, uid, ids, context=None):
        res = []
        for cat in self.browse(cr, uid, ids, context=context):
            names = [cat.name]
            pcat = cat.parent_id
            while pcat:
                names.append(pcat.name)
                pcat = pcat.parent_id
            res.append((cat.id, ' / '.join(reversed(names))))
        return res

    def _name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    # Localizar las ofertas asociadas a los grupos de productos.
    def _get_offer_ids(self, cr, uid, ids, name, args, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):

            offer_obj = self.pool.get('product.offer')
            all_offer_ids = offer_obj.search(cr, uid, [], context=context)
            all_offer = offer_obj.browse(cr, uid, all_offer_ids, context=context)

            offer_ids = []
            for offer in all_offer:

                # Grupo de productos.
                if record.id == offer.product_offer_group_id.id:
                    offer_ids.append(offer.id)

            res[record.id] = list(set(offer_ids))

        return res


    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'complete_name': fields.function(_name_get_fnc, type="char", string='Name'),
        'parent_id': fields.many2one('product.offer.group','Parent Group', select=True),
        'child_id': fields.one2many('product.offer.group', 'parent_id', string='Children groups'),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of product groups."),

        'image': fields.binary("Image",
            help="This field holds the image used as image for the group, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'product.offer.group': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of the group. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized image", type="binary", multi="_get_image",
            store={
                'product.offer.group': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of the group. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),

        'product_tmpl_ids': fields.many2many('product.template', 'product_template_product_offer_group_rel','product_tmpl_id', 'product_offer_group_id', string='Productos'),
        'product_offer_line_ids': fields.one2many('product.offer.line', 'product_offer_group_id', string='Condiciones', copy=True, store=True),

        'active': fields.boolean('Active'),

        'offer_ids': fields.function(_get_offer_ids, type='one2many', relation="product.offer", string="Ofertas del producto"),

    }
    _defaults = {
        'sequence': 1,
        'active' : True
    }
