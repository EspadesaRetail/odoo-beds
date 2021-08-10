# -*- coding: utf-8 -*-
import sys
import base64
import werkzeug
import werkzeug.urls
import locale
from openerp import SUPERUSER_ID
from openerp import http
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slugify

##from openerp.addons.web.controllers.main import login_redirect
from openerp.tools import html_escape as escape
from openerp.addons.website_sale.controllers.main import *
from openerp.osv import osv

import math
import json
import logging
_logger = logging.getLogger(__name__)


class beds_website_franquiciasbeds(http.Controller):

    @http.route([
        '/form/franquiciasbeds',
    ], type='http', auth="public", website=True)
    def franquiciasbeds(self, **kw):
        cr, uid, context = request.cr, request.uid, request.context

        keep = QueryURL('/form/franquiciasbeds')

        request.context.update({'show_address': True})

        return request.website.render("beds_franquicias.franquiciasbeds")

    def create_lead(self, request, values, kwargs):
        """ Allow to be overrided """
        cr, context = request.cr, request.context
        return request.registry['crm.lead'].create(cr, SUPERUSER_ID, values, context=dict(context, mail_create_nosubscribe=True))

    def preRenderThanks(self, values, kwargs):
        """ Allow to be overrided """
        company = request.website.company_id

        keep = QueryURL('/form/franquiciasbeds', search='')

        return {
            'keep' : keep,
            'search' : '',
            'values': values,
            'kwargs': kwargs,
        }

    def get_contactus_response(self, values, kwargs):
        values = self.preRenderThanks(values, kwargs)
        return request.website.render(kwargs.get("view_callback", "beds_theme.contactus_thanks"), values)

    @http.route(['/form/contacto_franquiciasbeds',], type='http', auth="public", website=True)
    def contactus(self, **kwargs):
        def dict_to_str(title, dictvar):
            ret = "\n\n%s" % title
            for field in dictvar:
                ret += "\n%s" % field
            return ret

        _TECHNICAL = ['show_info', 'view_from', 'view_callback']  # Only use for behavior, don't stock it
        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id', 'active']  # Allow in description
        _REQUIRED = ['name', 'contact_name', 'email_from', 'description']  # Could be improved including required from model

        post_file = []  # List of file to add to ir_attachment once we have the ID
        post_description = []  # Info to add after the message
        values = {}

        values['medium_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID, 'crm.crm_medium_website')
        values['section_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID, 'website.salesteam_website_sales')

        values["email_cc"] = 'bedsonline@tiendasbeds.es'

        # Add contact_name2 to contact_name.
        if kwargs.get("contact_name2"):
            kwargs["contact_name"] = kwargs.get("contact_name2") + ", " + kwargs.get("contact_name")
            kwargs.pop("contact_name2", None)

        for field_name, field_value in kwargs.items():
            if hasattr(field_value, 'filename'):
                post_file.append(field_value)
            elif field_name in request.registry['crm.lead']._fields and field_name not in _BLACKLIST:
                values[field_name] = field_value
            elif field_name not in _TECHNICAL:  # allow to add some free fields or blacklisted field like ID
                post_description.append("%s: %s" % (field_name, field_value))

        if "name" not in kwargs:
            values["name"] = "Formulario de contacto Franquicias Bed's"

        # fields validation : Check that required field from model crm_lead exists
        error = set(field for field in _REQUIRED if not values.get(field))

        if error:
            values = dict(values, error=error, kwargs=kwargs.items(),keep=None,search='')
            return request.website.render(kwargs.get("view_from"), values)

        # description is required, so it is always already initialized
        #if post_description:
        #    values['description'] += dict_to_str(_("Custom Fields: "), post_description)

        if kwargs.get("show_info"):
            post_description = []
            environ = request.httprequest.headers.environ
            post_description.append("%s: %s" % ("IP", environ.get("REMOTE_ADDR")))
            post_description.append("%s: %s" % ("USER_AGENT", environ.get("HTTP_USER_AGENT")))
            post_description.append("%s: %s" % ("ACCEPT_LANGUAGE", environ.get("HTTP_ACCEPT_LANGUAGE")))
            post_description.append("%s: %s" % ("REFERER", environ.get("HTTP_REFERER")))
            values['description'] += dict_to_str(_("Environ Fields: "), post_description)

        lead_id = self.create_lead(request, dict(values, user_id=False), kwargs)
        values.update(lead_id=lead_id)
        if lead_id:
            for field_value in post_file:
                attachment_value = {
                    'name': field_value.filename,
                    'res_name': field_value.filename,
                    'res_model': 'crm.lead',
                    'res_id': lead_id,
                    'datas': base64.encodestring(field_value.read()),
                    'datas_fname': field_value.filename,
                }
                request.registry['ir.attachment'].create(request.cr, SUPERUSER_ID, attachment_value, context=request.context)


            # mail
            #.send_forum_validation_email(request.cr, request.uid, request.uid, forum_id=forum_id, context=request.context)
            self.send_email_form(request.cr, request.uid,lead_id=lead_id)

        return self.get_contactus_response(values, kwargs)



    def send_email_form(self, cr, uid, lead_id):
        cr, uid, context = request.cr, request.uid, request.context

        template_obj = request.registry['email.template']
        template_id = template_obj.search(cr,SUPERUSER_ID,[('name','=','Formulario de franquiciasbeds')])

        if template_id:
            #_logger.debug("TEMPLATE FOUND")
            template_obj.send_mail(cr, SUPERUSER_ID, template_id[0], lead_id,context=context)
        return True
