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

import pytz
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT


try:
    from Crypto.Cipher import DES
    #from Crypto.Cipher import DES3
except ImportError:
    _logger.info("Missing dependency (pycrypto). See README.")



class AcquirerSequence(models.Model):
    _inherit = 'payment.acquirer'

    _order = "sequence, name"

    sequence = fields.Integer(string='Sequence', help="Gives the sequence order when displaying a list of acquirer payment.")

    _defaults = {
        'sequence': 10,
    }


class AcquirerStripe(models.Model):
    _inherit = 'payment.acquirer'

    def _get_stripe_urls(self, environment):
        """ Stripe URLs
        """
        if environment == 'prod':
            return {
                'stripe_form_url':
                'http://localhost:8069/',
            }
        else:
            return {
                'stripe_form_url':
                'http://localhost:8069/',
            }

    @api.model
    def _get_providers(self):
        providers = super(AcquirerStripe, self)._get_providers()
        providers.append(['stripe', 'Stripe'])
        return providers

    stripe_merchant_url = fields.Char('Merchant URL',
                                      required_if_provider='stripe')
    stripe_merchant_name = fields.Char('Merchant Name',
                                       required_if_provider='stripe')
    stripe_merchant_titular = fields.Char('Merchant Titular',
                                          required_if_provider='stripe')
    stripe_secret_key = fields.Char('Secret Key',
                                    required_if_provider='stripe')
    stripe_currency = fields.Char('Currency', default='eur',
                                  required_if_provider='stripe')
    stripe_transaction_type = fields.Char('Transtaction Type', default='0',
                                          required_if_provider='stripe')


    stripe_url_reply = fields.Char('Merchant URL Reply',
                                      required_if_provider='stripe')

    stripe_template = fields.Char('Merchant Template',
                                      required_if_provider='stripe')

    send_quotation = fields.Boolean('Send quotation', default=True)

    def _url_encode64(self, data):
        data = unicode(base64.encodestring(data), 'utf-8')
        return ''.join(data.splitlines())

    def _url_decode64(self, data):
        return json.loads(base64.b64decode(data))

    # Calcular el xor de los bloqes de datos.
    def sxor(self,s1,s2):
        # convert strings to a list of character pair tuples
        # go through each tuple, converting them to ASCII code (ord)
        # perform exclusive or on the ASCII code
        # then convert the result back to ASCII (chr)
        # merge the resulting array of characters as a string
        return ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(s1,s2))


    def cf_mac(self, sk, data):


        # Obtener las claves de izquierda y derecha, partiendo de una cadena en hexadecimal
        lk = sk[:16].decode("hex")
        rk = sk[16:32].decode("hex")

        # Añadir el caracter \x80 como último carácter.
        data = data.encode("utf-8") + b'\x80'

        # Añadir ceros al final hasta conseguir bloques completos.
        blocks = len(data) % 8
        zeros = blocks and (b'\0' * (8 - blocks)) or ''
        data += zeros

        # Obtener los bloques de datos.
        block=[]
        for i in range(len(data) / 8):
            s = i*8
            block.append(data[s:s+8])

        # Cifrado con DES, la doc. dice que tiene que ser DES3, pero la clave que se proporciona es insuficiente para ese tipo de cifrado.
        # hademas hacer xor de los bloques con cada resultado.
        # Cifrado izquierda.
        cipher = DES.new(key=lk , mode=DES.MODE_ECB)

        res = block[0]
        count = 1
        while (count < len(block)):
            res = cipher.encrypt(res)
            res = self.sxor(res, block[count])
            count = count + 1

        res = cipher.encrypt(res)

        # Descifrado derecha
        cipher_right = DES.new(key=rk , mode=DES.MODE_ECB)
        res = cipher_right.decrypt(res)


        # Cifrado izquierda.
        res = cipher.encrypt(res)

        # Devolver 4 dígitos en hexadecimal.
        res = res[:4].encode("hex").upper()
        print "RESULTADO hex:" + res
        return res





    # obtiene los datos utilizados para calcular el valor MAC.
    def cf_data_mac(self, tx_values):
        data += tx_values['CF_User']
        data += tx_values['CF_Date']
        data += tx_values['CF_Time']
        data += tx_values['CF_Amount']
        data += tx_values['CF_Currency']
        data += tx_values['CF_TicketNumber']
        return data




    def tz_now(self, tz_name = "Europe/Madrid"):
        utc_timestamp = pytz.utc.localize(datetime.now(), is_dst=False)  # UTC = no DST
        return utc_timestamp.astimezone(pytz.timezone(tz_name))


    @api.model
    def stripe_form_generate_values(self, id, partner_values, tx_values):
        acquirer = self.browse(id)
        stripe_tx_values = dict(tx_values)

        now = self.tz_now()

        stripe_tx_values.update({
            'CF_XtnType' : 'V',
            'CF_User' : acquirer.stripe_merchant_code,
            'CF_Date' : now.strftime("%d%m%Y"),
            'CF_Time' : now.strftime("%H%M%S"),
            'CF_Amount' : str(int(round(tx_values['amount'] * 100))),
            'CF_Currency' : acquirer.stripe_currency or '978',
            'CF_TicketNumber' : tx_values['reference'],
            'CF_Lang' : acquirer.stripe_merchant_lang or 'es',
            'CF_UrlReply' : acquirer.stripe_url_reply,
            'CF_Template' : acquirer.stripe_template,
            'CF_SetPartialAmount' : 0,
        })


        #_logger.debug("CONEXFLOW TX_VALUES:" + str(conexflow_tx_values))


        # Calcular la MAC
        data = self.cf_data_mac(stripe_tx_values)
        mac = self.cf_mac(acquirer.stripe_secret_key, data)

        _logger.debug("STRIPE:" + "\nKEY: " + acquirer.stripe_secret_key + "\nDATA: " + data + "\nMAC: " + mac)

        stripe_tx_values.update({
            'CF_MAC' : mac,
        })


        return partner_values, stripe_tx_values

    @api.multi
    def stripe_get_form_action_url(self):
        return self._get_stripe_urls(self.environment)['stripe_form_url']

    def _product_description(self, order_ref):
        sale_order = self.env['sale.order'].search([('name', '=', order_ref)])
        res = ''
        if sale_order:
            description = '|'.join(x.name for x in sale_order.order_line)
            res = description[:125]
        return res


class TxStripe(models.Model):
    _inherit = 'payment.transaction'

    stripe_txnid = fields.Char('Transaction ID')

    def merchant_params_json2dict(self, data):
        parameters = data.get('Ds_MerchantParameters', '').decode('base64')
        return json.loads(parameters)

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------
    # data : post parameters.
    # return tx : payment.transaction

    @api.model
    def _stripe_form_get_tx_from_data(self, data):
        """ Given a data dict coming from stripe, verify it and
        find the related transaction record.
        """
        # Obtener los datos de vuelta.
        reference = data.get('CF_TicketNumber', None)   # Rerencia del pedido.
        mac = data.get('CF_MAC', None)                  # MAC Asociada a la transacción.



        if not reference:
            error_msg = 'Stripe: received data with missing reference (%s)' % (reference)
            _logger.error(error_msg)
            raise ValidationError(error_msg)

        tx = self.search([('reference', '=', reference)])
        if not tx or len(tx) > 1:
            error_msg = 'Stripe: received data for reference %s' % (reference)
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
            error_msg = 'Conexflow: invalid shasign, received %s, computed %s,' \
                ' for data %s' % (shasign, shasign_check, data)
            _logger.error(error_msg)
            raise ValidationError(error_msg)
        """

        return tx

    @api.model
    def _stripe_form_get_invalid_parameters(self, tx, data):

        invalid_parameters = []

        if (tx.acquirer_reference and
                data.get('CF_TicketNumber')) != tx.acquirer_reference:
            invalid_parameters.append(
                ('CF_TicketNumber', data.get('CF_TicketNumber'),
                 tx.acquirer_reference))

        # No se puede validar el importe, ya que CF no retorna el importe cargado.
        return invalid_parameters

    @api.model
    def _stripe_form_validate(self, tx, data):

        status_code = data.get('CF_Result', '499')
        if (status_code == '000') or (status_code == '500'):

            msg = _('Stripe : %s. Autorización: %s. \(%s)') % (
                data.get('CF_Des_Result'),
                data.get('CF_NumAut'),
                "Tarjeta:" + data.get('CF_PAN')
            )

            tx.write({
                'state': 'done',
                'stripe_txnid': data.get('CF_NumAut'),
                'state_message': msg,
            })
            if tx.acquirer_id.send_quotation:
                tx.sale_order_id.force_quotation_send()
            return True


        error = _('Stripe: feedback error %s (%s). \nDatos recibidos:%s') % (
            data.get('CF_Des_Result'),
            data.get('CF_Result'),
            str({k: v for k, v in data.iteritems() if 'CF_' in k})
        )
        _logger.info(error)
        tx.write({
            'state': 'error',
            'state_message': error,

        })
        return False



    # TODO Creo que esto se puede borrar.
    @api.model
    def form_feedback(self, data, acquirer_name):
        res = super(TxStripe, self).form_feedback(data, acquirer_name)
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
