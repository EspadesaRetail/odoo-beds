# -*- coding: utf-8 -*-
import sys
import base64
import werkzeug
import werkzeug.urls
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug
##from openerp.addons.web.controllers.main import login_redirect
from openerp.tools import html_escape as escape
from openerp.addons.website_sale.controllers.main import *

import math

import json
import logging
_logger = logging.getLogger(__name__)


class beds_crm_claim_form(http.Controller):
    def claim_done(self, **kwargs):
        def dict_to_str(title, dictvar):
            ret = "\n\n%s" % title
            for field in dictvar:
                ret += "\n%s" % field
            return ret

        _OTHERS = ['contact_name','phone','shop', 'city', 'zip', 'shop', 'external_ref']
        _TECHNICAL = ['show_info', 'view_from', 'view_callback']  # Only use for behavior, don't stock it
        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id', 'active']  # Allow in description
        _REQUIRED = ['name', 'contact_name', 'email_from', 'description','solucion']  # Could be improved including required from model

        post_file = []  # List of file to add to ir_attachment once we have the ID
        post_description = []  # Info to add after the message
        values = {}

        values['medium_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID, 'crm.crm_medium_website')
        values['section_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID, 'website.salesteam_website_sales')


        for field_name, field_value in kwargs.items():
            if hasattr(field_value, 'filename'):
                post_file.append(field_value)
            elif (field_name in request.registry['crm.claim']._fields or field_name in _OTHERS) and field_name not in _BLACKLIST:
                values[field_name] = field_value
            elif field_name not in _TECHNICAL:  # allow to add some free fields or blacklisted field like ID
                post_description.append("%s: %s" % (field_name, field_value))

        if "name" not in kwargs and values.get("contact_name"):
            values["name"] = values.get("contact_name")

        # fields validation : Check that required field from model crm_claim exists
        error = set(field for field in _REQUIRED if not values.get(field))

        if error:
            values = dict(values, error=error, kwargs=kwargs.items(),keep=None,search='')
            return request.website.render(kwargs.get("view_from"), values)

        # description is required, so it is always already initialized
        #if post_description:
        #    values['description'] += dict_to_str(_("Custom Fields: "), post_description)

        """"
        post_description = []
        environ = request.httprequest.headers.environ
        post_description.append("%s: %s" % ("IP", environ.get("REMOTE_ADDR")))
        post_description.append("%s: %s" % ("USER_AGENT", environ.get("HTTP_USER_AGENT")))
        post_description.append("%s: %s" % ("ACCEPT_LANGUAGE", environ.get("HTTP_ACCEPT_LANGUAGE")))
        post_description.append("%s: %s" % ("REFERER", environ.get("HTTP_REFERER")))
        values['description'] += dict_to_str(_("Environ Fields: "), post_description)
        """

        claim_id = self.create_claim(request, dict(values, user_id=False), kwargs)
        values.update(claim_id=claim_id)

        if claim_id:
            for field_value in post_file:
                attachment_value = {
                    'name': field_value.filename,
                    'res_name': field_value.filename,
                    'res_model': 'crm.claim',
                    'res_id': claim_id,
                    'datas': base64.encodestring(field_value.read()),
                    'datas_fname': field_value.filename,
                }
                request.registry['ir.attachment'].create(request.cr, SUPERUSER_ID, attachment_value, context=request.context)

            # mail
            self.send_email_form(request.cr, request.uid,claim_id=claim_id)

        return self.get_contactus_response(values, kwargs)

    def create_claim(self, request, values, kwargs):
        cr, uid, context = request.cr, request.uid, request.context
        Partner = request.registry['res.partner']

        _logger.debug("VALUES: " + str(values))

        partner_id = Partner.search(cr,uid,[('email','=',values['email_from'])], limit=1)
        if not partner_id:
            partner_id = Partner.create(cr, SUPERUSER_ID, {
                'name' : values['contact_name'],
                'phone' : values.get('phone', False),
                'email': values['email_from'],
                'city' : values.get('city', False),
                'zip' : values.get('zip', False),
            })
        else:
            partner_id = partner_id[0]

        values['name'] = values['contact_name']

        values['partner_id'] = partner_id
        values['partner_phone'] = values.get('phone', False)

        return request.registry['crm.claim'].create(cr, SUPERUSER_ID, values, context=dict(context, mail_create_nosubscribe=True))




    def send_email_form(self, cr, uid, claim_id):
        cr, uid, context = request.cr, request.uid, request.context

        template_obj = request.registry['email.template']
        template_id = template_obj.search(cr,SUPERUSER_ID,[('name','=','Reclamación')])

        if template_id:
            #_logger.debug("TEMPLATE FOUND")
            template_obj.send_mail(cr, SUPERUSER_ID, template_id[0], claim_id,context=context)
        return True


    @http.route(['/form/reclamacion'], type='http', auth="public", website=True)
    def claim_form(self, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context


        # Procesar el formulario de reclamación
        if 'view_from' in kwargs:
            return self.claim_done(**kwargs)

        keep = QueryURL('/', search='')

        values = {
            'content' : None,
            'keep' : keep,
            'category' : None,
            'search' : None,
            'zip' : None,
            'description' : None,


        }

        for field in ['description', 'phone', 'contact_name','contact_name2', 'email_from', 'name','city','zip','shop','external_ref','solucion',]:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())

        return request.website.render("beds_crm_claim.reclamacion", values)

    def preRenderThanks(self, values, kwargs):
        """ Allow to be overrided """
        company = request.website.company_id

        keep = QueryURL('/shop', search='')

        return {
            'keep' : keep,
            'search' : '',
            'values': values,
            'kwargs': kwargs,
        }

    def get_contactus_response(self, values, kwargs):
        values = self.preRenderThanks(values, kwargs)
        return request.website.render(kwargs.get("view_callback", "beds_theme.contactus_thanks"), values)
