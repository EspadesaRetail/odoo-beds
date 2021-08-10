# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow
import logging
_logger = logging.getLogger(__name__)


class sale_order(osv.osv):
    _inherit = 'sale.order'


    # Actualiza los descuentos asociados a cada producto de las líneas del pedido.
    def _cart_update(self, cr, uid, ids, product_id=None, line_id=None, add_qty=0, set_qty=0, context=None, **kwargs):
        _logger.debug("_CART_UPDATE")
        values = super(sale_order, self)._cart_update(
            cr, SUPERUSER_ID, ids, product_id, line_id, add_qty, set_qty, context, **kwargs)


        for so in self.browse(cr, SUPERUSER_ID, ids, context=context):

            #_logger.debug("*****************************************************************")
            #_logger.debug("_CART_UPDATE: %s " % str(values) )
            #_logger.debug("_CART_UPDATE ORDER.PRICELIST_ID: %s " % str(so.pricelist_id.id) )

            for line in so.order_line:
                if line.id == values['line_id']:

                    # Si es una promoción no se actualiza nada.
                    if not line.offer_id:
                        line.lst_price = line.product_id.lst_price
                        line.lst_discount = line.product_id.lst_discount
                        line.lst_discount_offer = line.product_id.lst_discount_offer

                        # Calcular el precio unitario, una vez aplicados los descuentos.
                        line.price_unit = line.discounted_price


                        #_logger.debug("CART_UPDATE_LINE LST_PRICE: " + str(line.lst_price))
                        #_logger.debug("CART_UPDATE_LINE LST_DISCOUNT: " + str(line.lst_discount))
                        #_logger.debug("CART_UPDATE_LINE LST_DISCOUNT_OFFER: " + str(line.lst_discount_offer))
                        #_logger.debug("CART_UPDATE_LINE PRICE_UNIT: " + str(line.price_unit))


            # TODO Mover esto a la actualiación del pedido, incluso desde dentro de odoo.
            # Actualizar el tema de recogidas.
            so.update_remove_old_products()

        return values


    # Indica que se puede usar el pago parcial.
    def _allow_partial_payment(self, cr, uid, ids, name, arg, context=None):

        # colchones y bases.
        obj = self.pool['ir.model.data']
        allow_partial_payment_ids = []
        allow_partial_payment_ids.append(obj.xmlid_to_res_id(cr, uid, 'beds_model.categ_colchones', raise_if_not_found=True))
        allow_partial_payment_ids.append(obj.xmlid_to_res_id(cr, uid, 'beds_model.categ_bases', raise_if_not_found=True))
        allow_partial_payment_ids.append(obj.xmlid_to_res_id(cr, uid, 'beds_model.categ_sillones', raise_if_not_found=True))

        res = {}
        for sale_order in self.browse(cr, SUPERUSER_ID, ids, context=context):
            allow = False
            for line in sale_order.order_line:

                if line.product_id.product_tmpl_id.public_categ_ids:
                    for public_category in line.product_id.product_tmpl_id.public_categ_ids:
                        pc = public_category
                        if public_category.parent_id:
                            pc = public_category.parent_id
                        allow = allow or pc.id in allow_partial_payment_ids

            res[sale_order.id] = allow
        return res


    # Ver si se pueden retirar artículos de descanso.
    def _allow_remove_old_products(self, cr, uid, ids, name, arg, context=None):

        # colchones y bases.
        obj = self.pool['ir.model.data']
        allow_remove_old_products = []
        allow_remove_old_products.append(obj.xmlid_to_res_id(cr, uid, 'beds_model.categ_colchones', raise_if_not_found=True))
        allow_remove_old_products.append(obj.xmlid_to_res_id(cr, uid, 'beds_model.categ_bases', raise_if_not_found=True))
        allow_remove_old_products.append(obj.xmlid_to_res_id(cr, uid, 'beds_model.categ_sillones', raise_if_not_found=True))

        res = {}
        for sale_order in self.browse(cr, SUPERUSER_ID, ids, context=context):
            allow = False
            for line in sale_order.order_line:
                if line.product_id.product_tmpl_id.public_categ_ids:
                    for public_category in line.product_id.product_tmpl_id.public_categ_ids:
                        pc = public_category
                        if public_category.parent_id:
                            pc = public_category.parent_id
                        allow = allow or pc.id in allow_remove_old_products

            res[sale_order.id] = allow
        return res

    # Calcular cuantos artículos se pueden retirar.
    def _qty_remove_old_products(self, cr, uid, ids, name, arg, context=None):

        # colchones y bases.
        obj = self.pool['ir.model.data']
        allow_remove_old_products = []
        allow_remove_old_products.append(obj.xmlid_to_res_id(cr, uid, 'beds_model.categ_colchones', raise_if_not_found=True))
        allow_remove_old_products.append(obj.xmlid_to_res_id(cr, uid, 'beds_model.categ_bases', raise_if_not_found=True))
        allow_remove_old_products.append(obj.xmlid_to_res_id(cr, uid, 'beds_model.categ_sillones', raise_if_not_found=True))

        res = {}
        for sale_order in self.browse(cr, SUPERUSER_ID, ids, context=context):
            qty = 0
            for line in sale_order.order_line:
                allow = False

                if line.product_id.product_tmpl_id.public_categ_ids:
                    for public_category in line.product_id.product_tmpl_id.public_categ_ids:
                        pc = public_category
                        if public_category.parent_id:
                            pc = public_category.parent_id
                        allow = allow or pc.id in allow_remove_old_products

                    if allow:
                        qty += line.product_uom_qty

            res[sale_order.id] = qty
        return res


    # Actualiza los datos relativos a la recogida de productos usados.
    def update_remove_old_products(self):
        cr, uid, context = self.env.cr, self.env.uid, {}

        _logger.debug("UPDATE_REMOVE_OLD_PRODUCTS")

        remove_old_products = self.remove_old_products

        line_obj = self.pool.get('sale.order.line')

        # Localizar el producto para la retirada.
        product_retirar_obj = self.pool.get('product.product')
        product_retirar_id = product_retirar_obj.search(cr,uid,[('default_code','=','RETUSADOS')])
        product_retirar_id = product_retirar_obj.browse(cr,uid,product_retirar_id)

        line_ids = line_obj.search(cr, uid, [('order_id', '=', self.id), ('is_remove_old_products_line', '=', True)],context=context)

        qty = self.qty_remove_old_products

        # Delete line if no remove old products.
        if not (self.allow_remove_old_products and remove_old_products) :
            line_obj.unlink(cr, uid, line_ids, context=context)

        # Crear la línea si es necesario.
        else:
            if not line_ids:

                values = {
                    'order_id': self.id,
                    'product_id': product_retirar_id.id,
                    'name': product_retirar_id.name,
                    'product_uom_qty' : qty,
                    'lst_price': product_retirar_id.lst_price,
                    'is_remove_old_products_line' : True

                }
                if self.order_line:
                    values['sequence'] = self.order_line[-1].sequence + 1

                res = line_obj.product_id_change(cr, uid, [self.id], self.pricelist_id.id, values['product_id'],
                                                     qty=1, uom=False, qty_uos=0, uos=False, name='', partner_id=self.partner_id.id,
                                                     lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None)

                line_ids = [line_obj.create(cr, uid, values, context=context)]

            # Actualizar si no hay que recoger.
            #line_ids = line_obj.search(cr, uid, [('order_id', '=', self.id), ('is_remove_old_products_line', '=', True)],context=context)
            line_id = line_obj.browse(cr, uid, line_ids[0], context=context)
            if line_id.product_uom_qty > qty or line_id.product_uom_qty < 1:
                line_id.write({'product_uom_qty': qty})

    _columns = {
        'payment_amount': fields.float(string='Amount to pay', digits_compute=dp.get_precision('Account') ),
        'allow_partial_payment': fields.function(_allow_partial_payment,type="boolean", string='Amount to pay'),
        'allow_remove_old_products': fields.function(_allow_remove_old_products,type="boolean", string='¿Permitir recoger productos de descanso?'),
        'qty_remove_old_products': fields.function(_qty_remove_old_products,type="integer", string='Numero de árticulos viejos que se puenden retirar.'),
        'remove_old_products': fields.boolean('Recoger productos de descanso'),
    }

# Calcular el precio neto de una línea de producto, en base al proeducto.
class SaleOrderLine(osv.Model):
    _inherit = "sale.order.line"


    # Calcular el precio con descuentos.
    def _fnct_get_discounted_price(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, False)
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = (line.lst_price * (1.0 - (line.lst_discount or 0.0) / 100.0))
            if line.lst_discount_offer:
                res[line.id] = (res[line.id] * (1.0 - (line.lst_discount_offer) / 100.0))
        return res


    # Calcular el tipo de iva.
    @api.depends('product_id')
    def _get_tax_value(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, 0)
        for line in self.browse(cr, uid, ids, context=context):
            iva = 0.21
            res[line.id] = iva
        return res


    # Calcular base imponible de la línea.
    @api.depends('price_reduce', 'product_uom_qty', 'tax_value')
    def _get_tax_base(self, cr, uid, ids, field_name, args, context=None):
        res = dict.fromkeys(ids, 0)
        for line in self.browse(cr, uid, ids, context=context):
            price_reduce = round(line.price_reduce / (1+line.tax_value), 2)
            base = round(price_reduce * line.product_uom_qty,2)
            res[line.id] = base
        return res


    # borrar las líneas derivadas de promociones.
    def delete_lines_of_promo(self):
        cr, uid, context = self.env.cr, self.env.uid, {'chk_promo' : True}
        line_obj = self.pool.get('sale.order.line')
        line_id = self
        for offer_id in line_id.product_id.active_product_offer_ids:
            line_ids = line_obj.search(cr, uid, [('order_id', '=', line_id.order_id.id), ('offer_id', '=', offer_id.id),('offer_line_id','=',self.id)],context=context)
            line_obj.unlink(cr, uid, line_ids, context=context)


    # Add a new line to cart.
    def add_product_to_cart(self, order_id, product_id, price, qty=1, offer_id=None, offer_line_id=None):
        cr, uid, context = self.env.cr, self.env.uid, {}
        line_obj = self.pool.get('sale.order.line')

        values = {
            'order_id': order_id.id,
            'product_id': product_id.id,
            'name': product_id.name,
            'product_uom_qty' : qty,
            'price_unit': price,
            'lst_price': price,
            'offer_id' : offer_id.id,
            'offer_line_id' : offer_line_id.id,
        }
        if order_id.order_line:
            values['sequence'] = order_id.order_line[-1].sequence + 1

        context.update({'chk_recursion':True})

        return line_obj.create(cr, uid, values, context = context)




    _columns = {
        'lst_price': fields.float('Precio bruto', digits_compute= dp.get_precision('Product Price'), readonly=True, states={'draft': [('readonly', False)]}),

        # Sirve para guardar el valor utilizado en el descuento y poder enviarlo a beds con el pedido.
        'lst_discount': fields.float('Public discount (%)', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),
        'lst_discount_offer': fields.float('Public discount offer(%)', digits_compute= dp.get_precision('Discount'), readonly=True, states={'draft': [('readonly', False)]}),
        'discounted_price': fields.function(_fnct_get_discounted_price, string='Discounted price', type='float', digits_compute=dp.get_precision('Product Price')),
        'tax_value': fields.function(_get_tax_value, string='Tipo de iva', type='float', store=True),
        'tax_base': fields.function(_get_tax_base, string='Base imponible', type='float', store=True, digits_compute=dp.get_precision('Account')),

        'is_remove_old_products_line': fields.boolean('Es una linea de recogida de usados.'),
        'offer_id': fields.many2one('product.offer', 'Promoción', help='Promoción aplicada'),
        'offer_line_id': fields.many2one('sale.order.line', 'Línea promocionada', help='Línea del pedido que genera la oferta'),
        
        'pack_id': fields.many2one('product.pack', 'Pack', help='Línea asociada a un pack'),
        'pack_sequence': fields.integer('Sequencia de packs en un pedido', help="Permite borrar todas las líneas de un pack"),


    }

    _defaults = {
        'lst_discount_offer': 0,
        'is_remove_old_products_line' : False,
    }
