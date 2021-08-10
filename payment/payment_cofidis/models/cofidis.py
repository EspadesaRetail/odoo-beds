# -*- coding: utf-8 -*-
import hashlib
import hmac
import base64
import logging
import json
import time
from openerp import models, fields, api, _
from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.addons import decimal_precision as dp
from openerp.tools.float_utils import float_compare
from openerp import exceptions

_logger = logging.getLogger(__name__)



class AcquirerSequence(models.Model):
    _inherit = 'payment.acquirer'

    _order = "sequence, name"
    
    sequence = fields.Integer(string='Sequence', help="Gives the sequence order when displaying a list of acquirer payment.")
    
    _defaults = {
        'sequence': 10,
    }


class AcquirerCofidis(models.Model):
    _inherit = 'payment.acquirer'

    def _get_cofidis_urls(self, environment):
        """ Cofidis URLs
        """
        if environment == 'prod':
            return {
                'cofidis_form_url':
                'https://www.cofidisonline.cofidis.es/FinanciacionEstandar/bienvenido.do',
            }
        else:
            return {
                'cofidis_form_url':
                'https://rqt-www.cofidisonline.cofidis.es/FinanciacionEstandar/bienvenido.do',
            }

    @api.model
    def _get_providers(self):
        providers = super(AcquirerCofidis, self)._get_providers()
        providers.append(['cofidis', 'Cofidis'])
        return providers

    cofidis_merchant_url = fields.Char('Merchant URL',
                                      required_if_provider='cofidis')
    cofidis_merchant_name = fields.Char('Merchant Name',
                                       required_if_provider='cofidis')
    cofidis_merchant_titular = fields.Char('Merchant Titular',
                                          required_if_provider='cofidis')
    cofidis_merchant_code = fields.Char('Merchant code',
                                       required_if_provider='cofidis')
    cofidis_merchant_product = fields.Char('Cofidis Product',
                                              required_if_provider='cofidis')
    cofidis_url_reply = fields.Char('Merchant URL Reply',
                                       required_if_provider='cofidis')
    
    cofidis_minimum_funding = fields.Char('Minimum funding',required_if_provider='cofidis')
    cofidis_maximum_funding = fields.Char('Maximum funding',required_if_provider='cofidis')
                                              
    """                                          
    cofidis_secret_key = fields.Char('Secret Key',
                                    required_if_provider='cofidis')
    cofidis_terminal = fields.Char('Terminal', default='1',
                                  required_if_provider='cofidis')
    cofidis_currency = fields.Char('Currency', default='978',
                                  required_if_provider='cofidis')
    cofidis_transaction_type = fields.Char('Transtaction Type', default='0',
                                          required_if_provider='cofidis')
    cofidis_merchant_data = fields.Char('Merchant Data')
    cofidis_merchant_lang = fields.Selection([('es', 'Castellano'),
                                             ('en', 'Inglés'),
                                             ('CA', 'Catalán'),
                                             ('fr', 'Francés'),
                                             ('de', 'Alemán'),
                                             ('nl', 'Holandés'),
                                             ('IT', 'Italiano'),
                                             ('SV', 'Sueco'),
                                             ('pt', 'Portugués'),
                                             ('pl', 'Polaco'),
                                             ('GL', 'Gallego'),
                                             ('eu', 'Euskera'),
                                             ], 'Merchant Consumer Language',
                                            default='es')

    
    cofidis_template = fields.Char('Merchant Template',
                                      required_if_provider='cofidis')
    """
    
    
    
    send_quotation = fields.Boolean('Send quotation', default=True)

    def _url_encode64(self, data):
        data = unicode(base64.encodestring(data), 'utf-8')
        return ''.join(data.splitlines())

    def _url_decode64(self, data):
        return json.loads(base64.b64decode(data))

    @api.model
    def cofidis_form_generate_values(self, id, partner_values, tx_values):
        
        def format_values(p):
            v = "{0:07.2f}".format(p)
            _logger.debug("format_values: " + str(v))
            v = v.replace('.',',')
            return v
            
        
        acquirer = self.browse(id)
        cofidis_tx_values = dict(tx_values)

        # Desglosar los apellidos según protocolo Cofidis.
        nombre = partner_values['last_name']
        apellidos = partner_values['first_name']
        apellido1=''
        apellido2=''
        t = apellidos.split()
        if len(t) > 0:
            apellido1 = t[0]
            if len(t) > 1:
                apellido2 = ' '.join(t[1:])


        #>>> print("{0:07.2f}".format(round(a,2)))
        #0030.50

        nf = '{num:{fill}{width}}'


        # Datos obligatorios.
        cofidis_tx_values.update({
        
            # Cuidado entre referencia / reference
            'referencia' : tx_values['reference'],
            'vendedor' : acquirer.cofidis_merchant_code,
            'producto' : acquirer.cofidis_merchant_product,
            'nombre' : nombre[:40],
            'apellidos' : apellidos[:40],
            'apellido1' : apellido1[:40],
            'apellido2' : apellido2[:40],
            
            'url_acept' : acquirer.cofidis_merchant_url + '/payment/cofidis/return',
            'url_rechaz' : acquirer.cofidis_merchant_url + '/payment/cofidis/reject',
            'url_confirm' : acquirer.cofidis_merchant_url + '/payment/cofidis/confirm',
            'url_error' : acquirer.cofidis_merchant_url + '/payment/cofidis/error',
            
            #'importe' : "%06d" % int(round(tx_values['amount'] * 100)),
            'importe' : format_values(tx_values['amount']),
            
            'carencia' : '0',
        })

        # Inicializar las lista de productos.
        for l in range(1,6):
            kcantidad = "cantidadCompra%s" % str(l) 
            kprecio = "precioCompra%s" % str(l) 
            kdescripcion = "descCompra%s" % str(l) 
            ktotal = "precioTotal%s" % str(l) 
            cofidis_tx_values.update({
                    kcantidad : '',
                    kprecio : '',
                    kdescripcion : '',
                    ktotal : '',
                })
        
        # Obtener la orden..
        tx = self.env['payment.transaction'].search([('reference', '=', tx_values['reference'])])
        order = tx.sale_order_id if tx else False
        if order:
            l = 1
            for line in order.order_line:
                kcantidad = "cantidadCompra%s" % str(l) 
                kprecio = "precioCompra%s" % str(l) 
                kdescripcion = "descCompra%s" % str(l) 
                ktotal = "precioTotal%s" % str(l) 
                cofidis_tx_values.update({
                    kcantidad : str(int(line.product_uom_qty)),
                    kprecio : format_values(line.price_unit),
                    kdescripcion : line.name[:27],
                    ktotal : format_values(line.price_subtotal),
                })
                
                l += 1
                if l>5:
                    break
            
        """
        'Cofidis_Date' : time.strftime("%d%m%Y"),
        'Cofidis_Time' : time.strftime("%H%M%S"),

        'Cofidis_Currency' : acquirer.cofidis_currency or '978',
        'Cofidis_Lang' : acquirer.cofidis_merchant_lang or 'es',

        'Cofidis_UrlReply' : acquirer.cofidis_url_reply,
        'Cofidis_Template' : acquirer.cofidis_template,
        'Cofidis_SetPartialAmount' : 0,
        """
        
        _logger.debug("COFIDIS_TX_VALUES: " + str(cofidis_tx_values))
        return partner_values, cofidis_tx_values

    @api.multi
    def cofidis_get_form_action_url(self):
        return self._get_cofidis_urls(self.environment)['cofidis_form_url']

    def _product_description(self, order_ref):
        sale_order = self.env['sale.order'].search([('name', '=', order_ref)])
        res = ''
        if sale_order:
            description = '|'.join(x.name for x in sale_order.order_line)
            res = description[:125]
        return res

class TxCofidis(models.Model):
    _inherit = 'payment.transaction'

    cofidis_txnid = fields.Char('Transaction ID')

    def merchant_params_json2dict(self, data):
        parameters = data.get('Ds_MerchantParameters', '').decode('base64')
        return json.loads(parameters)

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------
    # data : post parameters.
    # return tx : payment.transaction

    @api.model
    def _cofidis_form_get_tx_from_data(self, data):
        """ Given a data dict coming from cofidis, verify it and
        find the related transaction record. 
        """
        # Obtener los datos de vuelta.
        reference = data.get('reference', None)   # Rerencia del pedido.
        
        if not reference:
            error_msg = 'Cofidis: received data with missing reference (%s)' % (reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = 'Cofidis: received data for reference %s' % (reference)
            if not tx:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        # verify mac
        """
        #TODO
        if shasign_check != shasign:
            error_msg = 'Cofidis: invalid shasign, received %s, computed %s,' \
                ' for data %s' % (shasign, shasign_check, data)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        """
        
        return tx

    @api.model
    def _cofidis_form_get_invalid_parameters(self, tx, data):
        
        invalid_parameters = []
        
        if (tx.acquirer_reference and
                data.get('reference')) != tx.acquirer_reference:
            invalid_parameters.append(
                ('reference', data.get('reference'),
                 tx.acquirer_reference))

        # No se puede validar el importe, ya que Cofidis no retorna el importe cargado.
        return invalid_parameters
    
    @api.model
    def _cofidis_form_validate(self, tx, data):
        
        status_code = data.get('Cofidis_Result', '499')
        if (status_code == '000') or (status_code == '500'):

            msg = _('Cofidis : %s. Autorización: %s. \(%s)') % (
                data.get('Cofidis_Des_Result'),
                data.get('Cofidis_NumAut'),
                "Tarjeta:" + data.get('Cofidis_PAN')
            )
            
            tx.write({
                'state': 'done',
                'cofidis_txnid': data.get('Cofidis_NumAut'),
                'state_message': msg,
            })
            if tx.acquirer_id.send_quotation:
                tx.sale_order_id.force_quotation_send()
            return True

        
        error = _('Cofidis: feedback error %s (%s). \nDatos recibidos:%s') % (
            data.get('Cofidis_Des_Result'),
            data.get('Cofidis_Result'),
            str({k: v for k, v in data.iteritems() if 'Cofidis_' in k})
        )
        _logger.info(error)
        tx.write({
            'state': 'error',
            'state_message': error,
            
        })
        return False

        
        """
        if (status_code >= 101) and (status_code <= 202):
            # 'Payment error: code: %s.'
            tx.write({
                'state': 'pending',
                'cofidis_txnid': parameters_dic.get('Ds_AuthorisationCode'),
                'state_message': _('Error: %s (%s)') % (
                    parameters_dic.get('Ds_Response'),
                    parameters_dic.get('Ds_ErrorCode')
                ),
            })
            return True
        if (status_code == 912) and (status_code == 9912):
            # 'Payment error: bank unavailable.'
            tx.write({
                'state': 'cancel',
                'cofidis_txnid': parameters_dic.get('Ds_AuthorisationCode'),
                'state_message': _('Bank Error: %s (%s)') % (
                    parameters_dic.get('Ds_Response'),
                    parameters_dic.get('Ds_ErrorCode')
                ),
            })
            return True
        else:
            error = _('Cofidis: feedback error %s (%s)') % (
                parameters_dic.get('Ds_Response'),
                parameters_dic.get('Ds_ErrorCode')
            )
            _logger.info(error)
            tx.write({
                'state': 'error',
                'cofidis_txnid': parameters_dic.get('Ds_AuthorisationCode'),
                'state_message': error,
            })
            return False"""

    # TODO Creo que esto se puede borrar.            
    # si es así borrar también el del conexflow.
    @api.model
    def form_feedback(self, data, acquirer_name):
        res = super(TxCofidis, self).form_feedback(data, acquirer_name)
        #_logger.debug("CUSTOM FORM FEEDBACK")
        try:
            
            if res:
                tx_find_method_name = '_%s_form_get_tx_from_data' % acquirer_name
                if hasattr(self, tx_find_method_name):
                    tx = getattr(self, tx_find_method_name)(data)
                    return tx

        except Exception:
            return False
        return False

        