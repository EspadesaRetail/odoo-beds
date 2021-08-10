# -*- coding: utf-8 -*-
import traceback
from datetime import datetime
from datetime import timedelta
import json
import logging
from openerp import SUPERUSER_ID
from openerp import workflow
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _
from suds.client import Client

from openerp.addons.website.controllers.main import *
import decimal
import time
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

from urllib2 import urlopen
_logger = logging.getLogger(__name__)

from openerp import api
from openerp.osv import fields, osv

from urllib2 import urlopen
from lxml import etree



_logger = logging.getLogger(__name__)

"""
            except Exception as e:
                tb = traceback.format_exc()
                _logger.error("Error at update pricelist.\n%s" % str(e))
                _logger.error(tb)

                template_pool = self.pool['email.template']
                if not context:
                    context = {}

                current_user_id = self.pool['res.users'].browse(cr, uid, uid, context=context)
                local_context = context.copy()
                local_context.update({
                })
                template_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'cs_model', 'cron_update_pricelist')[1]
                mail_id = template_pool.send_mail(cr, uid, template_id, product_template_id.id, force_send=True, context=local_context)

                continue

"""


class product_beds_ws(osv.osv_memory):
    _name = "beds.ws.update.pricelist"
    _description = "Product web services"


    # Calculo de precampaña. Modifica los precios de tarifa para preparar una promoción específica.
    def _calcular_precios_precampana(self, product_id, precio_tarifa, dto):

        #filtrar por producto.
        # Excluir producto platino que está en oferta. CM11199
        #if product_id.default_code == "CM11199":
        #    return precio_tarifa,dto

        now = time.strftime('%Y%m%d')
        if now > '20180428':
            return precio_tarifa, dto

        tabla = [
            {"d":-1,"h":10.0, "r":0.1, "dto": 0.0},
            {"d":10.0,"h":15.0, "r":0.14, "dto": 1.0},
            {"d":15.0,"h":25.0, "r":0.12, "dto": 13.0},
            {"d":25.0,"h":30.0, "r":0.11, "dto": 18.7},
            {"d":30.0,"h":40.0, "r":0.1, "dto": 30.0},
            {"d":40.0,"h":45.0, "r":0.09, "dto": 36.0},
            {"d":45.0,"h":50.0, "r":0.08, "dto": 42.0},
            {"d":50.0,"h":55.0, "r":0.075, "dto": 47.5},
            {"d":55.0,"h":60.0, "r":0.07, "dto": 53.0},
            {"d":60.0,"h":65.0, "r":0.06, "dto": 59.0},
            {"d":65.0,"h":100.0, "r":0, "dto": 65.0},
        ]

        c = [x for x in tabla if (x["d"] < dto and x["h"] >= dto)]

        if not c:
            return precio_tarifa, dto

        r = 1.0 - c[0]["r"]
        descuento = c[0]["dto"]
        precio = round(float(precio_tarifa) / r,2)

        return precio, descuento







    # Permite actualizar los precios desde los servicios web de beds.
    def update_product_pricelist(self, cr, uid, ids=False, context=None):
        _logger.debug("Start product pricelist update.")

        obj = self.pool.get('product.template')

        # Cuando se llama desde la ventana.
        if context and 'active_ids' in context:
            ids = context.get('active_ids', [])
            _logger.info("Update pricelist for active ids %s" % str(ids))

        # Cuando se ejecuta el proceso en automático, se hace para todos los productos activos y publicados.
        else:
            ids = obj.search(cr, uid, [], order='date_last_update')
            _logger.info("Update pricelist for all products.")


        #url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url') + "/beds_model/static/wsdl/beds.wsdl"
        url = wsGetUrlWsdl(self,cr,uid,'wscodb')

        client = Client(url)


        # Obtener las versiones correspondientes a las tarifas de Peninsula, Baleares y Canarias.
        #price_version_id
        peninsula_version_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.ver0', raise_if_not_found=True)
        canarias_version_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.ver1', raise_if_not_found=True)
        baleares_version_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.ver2', raise_if_not_found=True)

        # recorrer los productos seleccionados.
        for product_template_id in obj.browse(cr, uid, ids):
            try:
                l = []

                # recorrer las variantes de los productos. La tarifa va por variante.
                for variant in product_template_id.product_variant_ids:
                    if variant.ean13:
                        # Recuperar los precios, para peninsula y canarias.
                        for tipo in ['P','C','B']:
                            l.append({
                                     'l01TIPO': tipo,
                                     'l01CBAR': variant.ean13,
                                     })


                # Hacer una llamada a ws para cada product_template, pero con todas las variantes.
                _logger.info("Request pricelist update (%s %s)." % (product_template_id.default_code,product_template_id.name))
                _logger.debug("WLISCBAR: " + str(l))
                res = client.service.wscodb({'WLISCBAR': l})
                #_logger.info("Receive pricelist update (%s %s)." % (product_template_id.default_code,product_template_id.name))
                #_logger.debug("DATOS DEL WS: " + str(res))

                obj_item = self.pool.get('product.pricelist.item')
                obj_product = self.pool.get('product.product')
                base_id = self.pool['ir.model.data'].xmlid_to_res_id(cr, uid, 'product.list_price', raise_if_not_found=True)

                res = [r for r in res.WLISCBAR if r.l01CBAR <> 0]

                for r in res:
                    codigo_barras = str(int(r.l01CBAR))

                    if r.l04ERR==0:
                        version = peninsula_version_id
                        if r.l01TIPO == 'C':
                            version = canarias_version_id

                        if r.l01TIPO == 'B':
                            version = baleares_version_id

                        # Hay que tener en cuenta el product_product que se está actualizando, ya que si hay grupos de productos
                        # El código de baras puede estár duplicado.

                        id = obj_item.search(cr, uid, [('product_tmpl_id','=',product_template_id.id),('product_id.ean13', '=', codigo_barras),('price_version_id','=',version)])

                        # Comprobar si hay algún cambio a nivel de descuentos por precampaña de oferta.
                        precio, descuento = self._calcular_precios_precampana(product_template_id, r.l02PREC, r.l03DTO,)

                        if id:
                            obj_item.write(cr, uid,id,{
                                'product_price': r.l02PREC,
                                'product_discount': descuento,    #r.l03DTO,
                                'product_tax_percentage': r.l05PORCIM,
                                'date_last_update' : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            })
                            _logger.info("Update pricelist (%s %s: %s %s)." % (product_template_id.default_code, codigo_barras, str(r.l02PREC),str(r.l03DTO)))

                        else:
                            # Localizar el producto.
                            product_ids = obj_product.search(cr, uid, [('product_tmpl_id','=',product_template_id.id),('ean13','=',codigo_barras)])

                            if product_ids:
                                obj_item.create(cr, uid,{
                                            'product_tmpl_id' : product_template_id.id,
                                            'product_id': product_ids[0],
                                            'price_version_id': version,
                                            'base' : base_id,
                                            'product_price': precio,
                                            'product_discount': r.l03DTO,
                                            'product_tax_percentage': r.l05PORCIM,
                                            'date_last_update' : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                            })
                                _logger.info("Create new pricelist (%s %s: %s %s)." % (r.l01TIPO, codigo_barras, str(r.l02PREC),str(r.l03DTO)))

                    else:
                        _logger.warning("Error when get the pricelist for (%s - %s). Error:%s" % (product_template_id.default_code, codigo_barras, r.l04ERR))
                        #raise osv.except_osv('Error!', "Error when get the pricelist for %s %s %s" % (r.l04ERR,codigo_barras,r.l02PREC,))

                    #else:
                    #   El ws de actualización, devuelve códigos no informados, por un asunto del AS-400.
                    #   _logger.debug("El código de barras no está informado.")

                # Actualizar el producto.
                product_template_id.write({
                            'date_last_update' : time.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                            })
                _logger.info("Update product: last_date_update. %s" % product_template_id.default_code)

                # Actualizar la fecha de última actualización.
                cr.commit()

            except Exception, e:
                _logger.error("Error ws %s" % str(e))
                continue

        _logger.info("End update product pricelist.")
        return {
            'type': 'ir.actions.act_window_close',
            'tag': 'reload',

        }


# WS de actualización de estado del pedido.
class sale_order_beds_ws(osv.osv_memory):
    _name = "beds.ws.sale.order.update.status"
    _description = "Sales Advance Payment Invoice"

    _columns = {
        'name': fields.char("Name"),
    }

    def sale_order_update_status(self, cr, uid, ids=False, context=None):

        obj = self.pool.get('sale.order')


        # Cuando se llama desde la ventana.
        if context:
            ids = context.get('active_ids', [])

        # Cuando se ejecuta el proceso en automático, se hace para todos los pedido pendientes
        else:
            # status: 1:Cancelado, 5: Completado.
            ids = obj.search(cr, uid, [('beds_pedido', '<>', None), ('beds_estado', '<>', 5), ('beds_estado', '<>', 1), ('state', 'in', ['manual', 'progress'])])

        # Enviar todos los pedidos seleccionados.
        for order in obj.browse(cr, uid, ids):

            if order.beds_pedido:
                try:
                    #url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'web.base.url') + "/ws/wsdl?dev=True"
                    url = wsGetUrlWsdl(self,cr,uid,'wssitu')
                    client = Client(url)
                    r = client.service.wssitu({'WSUPED':order.beds_pedido})

                    order.write({
                                'beds_estado':r.WESTADO,
                                'beds_fecha_entrega':r.WFECH,
                                'beds_situacion':r.WSITU,
                                })


                    _logger.info("ORDER_STATUS: " + str(r))

                except Exception as e:
                    _logger.error("Error %s" % e)

        return {
            'type': 'ir.actions.act_window_close',
            'tag': 'reload',

        }


# WS envío de pedidos.
class beds_ws_sale_order(osv.osv_memory):
    _name = "beds.ws.send.sale.order"


    def send_sale_order(self, cr, uid, ids=False, context=None):

        obj = self.pool.get('sale.order')


        # Cuando se llama desde la ventana.
        if context:
            ids = context.get('active_ids', [])

        # Cuando se ejecuta el proceso en automático, se hace para todos los pedido pendientes
        else:
            ids = obj.search(cr, uid, [('beds_pedido', '=', None), ('state', 'in', ['manual', 'progress'])])


        url = wsGetUrlWsdl(self,cr,uid,'wspedv')
        client = Client(url)

        for order in obj.browse(cr, uid, ids):


            # Compruebo que no ha sido enviado.
            if not order.beds_pedido and not order.beds_pedido_enviado:
                _logger.debug("ENVIANDO PEDIDO A BEDS: " + str(order.name))
                _logger.debug("DATE ORDER: " + str(order.date_order))
                _logger.debug("SHIPPING_PARTNER_ID: " + str(order.partner_shipping_id))

                txnid=''
                txtype = 'TR'

                if order.payment_tx_id.acquirer_id.provider:
                    provider = order.payment_tx_id.acquirer_id.provider.upper()
                    if provider == "CONEXFLOW":
                        txnid = order.payment_tx_id.conexflow_txnid
                        txtype = 'TC'

                # Pendiente COFIDIS.



                # Importe pagado.
                payment_amount = order.payment_tx_id.amount


                # Líneas de pedido.
                sum_neto = 0
                sum_total = 0
                portes = 0


                # TODO Gestionar el impuesto en canarias, dependiente de la composición de los materiales.

                lineas = []
                for line in order.order_line:

                    # Sumar las líneas de portes.
                    if line.product_id.name == "ENV" or line.product_id.default_code == "ENV" or line.is_delivery:
                        portes += round(line.price_unit, 2)
                        continue

                    # Descartar los portes y productos sin código de barras.
                    if not line.product_id.ean13:
                        continue

                    lst_price = round(line.lst_price / 1.21, 2)
                    price_unit = round(line.price_unit / 1.21, 2)
                    price_reduce = round(line.price_reduce / 1.21, 2)

                    lst_discount = line.lst_discount
                    lst_discount_offer = line.lst_discount_offer
                    neto = round(price_reduce * line.product_uom_qty,2)
                    total = round(line.price_reduce * line.product_uom_qty,2)
                    tax = round(total - neto,2)

                    _logger.debug("Linea " + line.product_id.name + " precio bruto:" + str(lst_price) + " dtos:" + str(lst_discount) +
                            (("+" + str(lst_discount_offer)) if lst_discount_offer>0 else "") +
                            " precio unit:" + str(price_reduce) + " cantidad:" + str(line.product_uom_qty) + " neto:" + str(neto) + " tax:" + str(tax)+ " total:" +str(total) )

                    sum_neto += neto
                    sum_total += total


                    lineas.append(
                        {
                            'l01CODB': line.product_id.ean13,
                            'l02CANT': line.product_uom_qty,
                            'l03PRECB': lst_price,
                            'l04DTO': lst_discount,
                            'l05DTOO': lst_discount_offer,
                            'l06PRECN': price_reduce,
                            'l07IMPN': neto,
                            'l08IMPIVA': tax,
                            'l09IMPTOT': total,
                            #'l10OFER': ' ',
                            'l11IVAP': 21,
                        }
                    )

                # Importe total del pedido
                sum_tax = round(sum_total - sum_neto,2)

                # Importe pendiente de pago.
                outstanding_amount = round(sum_total - payment_amount,2)


                _logger.debug("Pedido neto:" + str(sum_neto) + " tax:" + str(sum_tax) + " total:" + str(sum_total))
                _logger.debug("Pago " + str(payment_amount) + (" pendiente" + str(outstanding_amount ) if outstanding_amount >0 else ""))
                _logger.debug("Portes " + str(portes))



                # Calcular los impuestos del peiddo. Hay que tener en cuenta si hay portes.
                sum_tax = sum_total - sum_neto

                # Calcular los impuestos del peiddo cuando hay portes.
                # En pikolin, no validan cuando hay portes si la suma de las líneas coincide con el pedido.
                if portes > 0:
                    sum_neto = round(sum_neto + portes * 0.21, 2)
                    sum_total = sum_total + portes
                    sum_tax = sum_total - sum_neto

                # Componer los datos de entrada del ws para envío de pedidos.
                ped = {

                    # Datos de cliente:
                    'WLIS_PEDCLI': {

                        'l25SUPED': order.name,
                        'l26FECSOL': "",
                        #'l26FECSOL': "%s%s%s" % (order.date_order[0:4],order.date_order[5:7],order.date_order[8:10]),

                        'l01NOMCLI':order.partner_id.name1,
                        'l02APELLI':order.partner_id.name2,

                        # Dirección de facturación
                        'l12TIPVIAF':order.partner_id.street_type.code,
                        'l13DIRF': order.partner_id.street_name,
                        'l14NUMF': order.partner_id.street_number or '',
                        'l15ESCALF': (order.partner_id.street_esc and order.partner_id.street_esc[:2]) or '',
                        'l16PISOF': (order.partner_id.street_piso and order.partner_id.street_piso[:2]) or '',
                        'l17PUERTAF': (order.partner_id.street_puerta and order.partner_id.street_puerta[:2]) or '',
                        'l18CODPOSF': order.partner_id.zip or '' ,
                        'l19POBLACF': order.partner_id.city,
                        'l20PAISF': 'ES',

                        # Dirección de entrega
                        'l03TIPVIAE':order.partner_shipping_id.street_type.code,
                        'l04DIRE': order.partner_shipping_id.street_name,
                        'l05NUME': order.partner_shipping_id.street_number or '',
                        'l06ESCALE': (order.partner_shipping_id.street_esc and order.partner_shipping_id.street_esc[:2]) or '',
                        'l07PISOE': (order.partner_shipping_id.street_piso and order.partner_shipping_id.street_piso[:2]) or '',
                        'l08PUERTAE': (order.partner_shipping_id.street_puerta and order.partner_shipping_id.street_puerta[:2]) or '',
                        'l09CODPOSE': order.partner_shipping_id.zip or '',
                        'l10POBLACE': order.partner_shipping_id.city or '',
                        'l11PAISE': 'ES',

                        'LIMPCOB': payment_amount,
                        'LIMPPDTE': outstanding_amount,
                        'l35FCOBRO': txtype,                    # Forma de cobro TC, TR
                        'LNAUTO': txnid,                        # Autorización para cuando txtype = TC.

                        'l27PORTES': portes,
                        'l28NETO':  sum_neto,
                        'l29IMPIVA': sum_tax,
                        'l30IMPTOT': sum_total,
                        'l31RETUSA': order.remove_old_products and 'S' or 'N' ,
                        'l32OBSER': order.note[:60] if order.note else '',           # Observaciones al pedido.
                        'l33FECC': "%s%s%s" % (order.date_order[0:4],order.date_order[5:7],order.date_order[8:10]),
                        'l34HORAC': "%s%s%s" % (order.date_order[11:13],order.date_order[14:16],order.date_order[17:19]),

                        'l21TEL1': order.partner_id.phone,
                        'l23DNI': order.partner_id.vat[2:],
                        'l24EMAIL': order.partner_id.email,


                        },
                    'WLINPED': lineas,

                }

                _logger.info("Call BEDS.WSPEDV")
                _logger.info(str(ped))

                r = client.service.wspedv(ped)

                # Verificar el resultado del envío a bed's.
                if r and r.WERROR == 0:
                    order.write({
                                'beds_pedido':r.WPEDVENTA,
                                'beds_fecha_entrega':r.WFECHAP,
                                'beds_ws_res':r.WERROR,
                                'beds_ws_msg':"",
                                'beds_pedido_enviado':"S",
                                })

                else:
                    _logger.error("Error al enviar el pedido a bed's. Error: " + str(r.WERROR))
                    order.beds_ws_msg = r.WERRORD
                    order.beds_ws_res = str(r.WERROR)
                    order.beds_pedido_enviado = "S"



        return {
            'type': 'ir.actions.act_window_close',
            'tag': 'reload',

        }

# Obtener la url del wsdl
def wsGetUrlWsdl(self,cr,uid, service):
    obj_ws = self.pool.get('webservices.config.settings')
    ids = obj_ws.search(cr,SUPERUSER_ID,[('service','=',service)])

    url = None
    if ids:
        ws= obj_ws.browse(cr,uid,ids)[0]
        url = ws.source_host + ws.wsdl

    _logger.debug("WS URL:" + str(url))
    return url


class WebServices(osv.osv):
    _name = "webservices.config.settings"
    _description = "Web Services config settings"


    # Calculate the source ip.
    _columns = {
        'service': fields.char('Service'),
        'source_host': fields.char('Source ip'),
        'wsdl': fields.char('wsdl'),

    }

class web_services(WebServices):
    _inherit = 'webservices.config.settings'

    def saluta(self, cr, uid, ids, context=None):
        obj = self.pool.get('webservices.config.settings')
        ids = obj.search(cr,uid,[('service','=','saluta')])
        if ids:
            saluta = obj.browse(cr,uid,ids)[0]

        url = saluta.source_host + saluta.wsdl

        _logger.debug("WS URL: %s" % url)

        client = Client(url)
        r = client.service.saluta({'ISALUDA':'Hola'})
        _logger.debug("Call Web Service Hello, result: %s", r)

        return {
            'tag': 'reload',
        }
