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


class beds_website_tiendas(http.Controller):

    # Localiza la tienda más cercana, en función de unas coordenadas geo terrestres concretas.
    # A continuación se ejecuta un algoritmo para el calculo de la distancia terrestre más cercana.
    @http.route(['/locate/store'], type='json', auth="public", website=True)
    def locate_store(self, lat,lng, **kw):
        cr, uid, context = request.cr, request.uid, request.context

        _logger.debug(str(context))
        _logger.debug("Lat: %s , Lng:%s", lat,lng )

        partner_obj = request.registry['res.partner']
        domain = [('beds_shop', '=', True),('partner_latitude','!=',0)]
        partners_ids = partner_obj.search(cr, SUPERUSER_ID, domain, context=context)

        # Radio de la tierra.
        R = 6378.137

        distancia = sys.maxint
        store = None

        lat = float(lat)
        lng = float(lng)

        for partner in partner_obj.browse(cr, SUPERUSER_ID, partners_ids, context=context):

             rplat = float(partner.partner_latitude)
             rplng = float(partner.partner_longitude)

             dlat = math.radians(rplat - lat)
             dlng = math.radians(rplng - lng)
             a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat)) * math.cos(math.radians(rplat)) * math.sin(dlng / 2) * math.sin(dlng / 2)

             c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

             d = R * c

             if d < distancia:
                 distancia = d
                 store = partner

        r = {'location': ''}
        if store:
            r =  {
                'id' : store.id,
                'location': "%s<br/>%s %s" % (store.name, str(store.zip), store.city),
                'name':store.name,
                'street':store.street,
                'city':store.city,
                'zip':partner.zip
                }

        _logger.debug("Tienda cerca: " + r['location'])
        return r



class website_form(http.Controller):
    @http.route(['/form/franquicias'], type='http', auth="public", website=True)
    def franquicias(self, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context

        keep = QueryURL('/', search='')

        values = {
            'content' : None,
            'keep' : keep,
            'category' : None,
            'search' : None,
            'description' : None,

        }

        for field in ['description', 'partner_name', 'phone', 'contact_name','contact_name2', 'email_from', 'name','city']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())

        return request.website.render("beds_theme.franquicias", values)

    @http.route(['/form/trabaja-con-nosotros'], type='http', auth="public", website=True)
    def trabaja_con_nosotros(self, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context

        keep = QueryURL('/', search='')

        values = {
            'content' : None,
            'keep' : keep,
            'category' : None,
            'search' : None,
            'zip' : None,
            'description' : None,


        }

        for field in ['description', 'phone', 'contact_name','contact_name2', 'email_from', 'name','zip','state','area']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())

        return request.website.render("beds_theme.trabaja_con_nosotros", values)

    @http.route(['/form/contactar'], type='http', auth="public", website=True)
    def contactar_con_nosotros(self, **kwargs):
        cr, uid, context = request.cr, request.uid, request.context

        keep = QueryURL('/', search='')

        values = {
            'content' : None,
            'keep' : keep,
            'category' : None,
            'search' : None,
            'zip' : None,
            'description' : None,


        }

        for field in ['description', 'phone', 'contact_name', 'email_from', 'name','zip','state','area']:
            if kwargs.get(field):
                values[field] = kwargs.pop(field)
        values.update(kwargs=kwargs.items())

        return request.website.render("beds_theme.contactar_con_nosotros", values)

    def create_lead(self, request, values, kwargs):
        """ Allow to be overrided """
        cr, context = request.cr, request.context
        return request.registry['crm.lead'].create(cr, SUPERUSER_ID, values, context=dict(context, mail_create_nosubscribe=True))

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



    @http.route(['/form/contact'], type='http', auth="public", website=True)
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

        if "name" not in kwargs and values.get("contact_name"):
            values["name"] = values.get("contact_name")

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
        template_id = template_obj.search(cr,SUPERUSER_ID,[('name','=','Formulario de franquicias')])

        if template_id:
            #_logger.debug("TEMPLATE FOUND")
            template_obj.send_mail(cr, SUPERUSER_ID, template_id[0], lead_id,context=context)
        return True



    # Redirigir la página de contacto estandar.
    @http.route(['/page/contactus'], type='http', auth="public", website=True)
    def redirect_contact(self, **kwargs):
        return werkzeug.utils.redirect('/form/contactar', 301)
