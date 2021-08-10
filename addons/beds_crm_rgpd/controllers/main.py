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

import re


class beds_crm_rgpd_form(http.Controller):
    def unsubscribe_done(self, **kwargs):
        def dict_to_str(title, dictvar):
            ret = "\n\n%s" % title
            for field in dictvar:
                ret += "\n%s" % field
            return ret

        _OTHERS = ['selector']
        _TECHNICAL = ['show_info', 'view_from', 'view_callback']
        _BLACKLIST = ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id', 'active']
        _REQUIRED = ['phone','selector']

        post_description = []  # Info to add after the message
        values = {}

        values['list_id'] = request.registry['ir.model.data'].xmlid_to_res_id(request.cr, SUPERUSER_ID, 'beds_crm_rgpd.unsubscribe_list')
        values['opt_out'] = True

        for field_name, field_value in kwargs.items():
            if (field_name in request.registry['mail.mass_mailing.contact']._fields or field_name in _OTHERS) and field_name not in _BLACKLIST:
                values[field_name] = field_value
            elif field_name not in _TECHNICAL:  # allow to add some free fields or blacklisted field like ID
                post_description.append("%s: %s" % (field_name, field_value))

        # fields validation : Check that required field from model mail.mass_mailing.contact exists
        error = set(field for field in _REQUIRED if not values.get(field))

        if values["phone"]:
            expr_digito = re.compile('[0-9]')
            expr_mov_es = re.compile('[6|7]\d{8}')
            expr_mov_pt = re.compile('[9]\d{8}')
            if values["selector"] in "ES":
                if not expr_mov_es.match(values["phone"]) or len(values["phone"]) > 9:
                    error = 'phone'
            elif values["selector"] in "PT":
                if not expr_mov_pt.match(values["phone"]) or len(values["phone"]) > 9:
                    error = 'phone'
            else:
                for i in range(len(values["phone"])):
                    if not expr_digito.match(values["phone"][i]):
                        error = 'phone'
                        break

        if error:
            values = dict(values, error=error, kwargs=kwargs.items(),keep=None,search='')
            print(values)
            return request.website.render(kwargs.get("view_from"), values)

        values["name"] = "baja SMS"
        values["email"] = "bedsonline@tiendasbeds.es"
        contact_id = self.create_unsubscribe(request, values)

        return request.website.render("beds_crm_rgpd.unsubscribe_thanks", values)

    def create_unsubscribe(self, request, values):
        cr, uid, context = request.cr, request.uid, request.context

        record_fields = request.registry['mail.mass_mailing.contact']._fields
        for field_name in values.keys():
            if field_name not in record_fields:
                values.pop(field_name)

        _logger.debug("PASO 1.4 " + str(values))
        return request.registry['mail.mass_mailing.contact'].create(cr, SUPERUSER_ID, values)

    @http.route(['/form/baja'], type='http', auth="public", website=True)
    def unsubscribe_form(self, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context

        # Procesar el formulario de reclamación
        if 'view_from' in kwargs:
            return self.unsubscribe_done(**kwargs)

        keep = QueryURL('/', search='')

        values = {
            'content' : None,
            'keep' : keep,
            'category' : None,
            'search' : None,
            'zip' : None,
            'description' : None,


        }

        for field in ['phone', 'selector',]:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())

        return request.website.render("beds_crm_rgpd.unsubscribe", values)
