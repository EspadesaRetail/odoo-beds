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


class country_state(osv.osv):
    _inherit = 'res.country.state'

    def slug_name(self):
        return slugify(self.name)



class beds_website_tiendas(http.Controller):

    # Calcular el horario de apertura de tiendas.
    def schedule(self, partner):

        s1=s2=s3=s4=''

        if partner.monday_schedule:
            s1 = "%s: %s" % (_("Lunes"), partner.monday_schedule)
            if partner.weekly_schedule:
                s2 = "%s: %s" % (_("Martes-Viernes"), partner.weekly_schedule)
            if partner.saturday_schedule:
                s3 = "%s: %s" % (_("Sábado"), partner.saturday_schedule)

        else:
            if partner.weekly_schedule:
                s1 = "%s: %s" % (_("Lunes-Viernes"), partner.weekly_schedule)
            if partner.saturday_schedule:
                s2 = "%s: %s" % (_("Sábado"), partner.saturday_schedule)

        if partner.summer_schedule:
            s4 = "%s: %s" % (_("Verano"), partner.summer_schedule)

        return s1,s2,s3,s4

    @http.route([
        '/tiendas-beds',
        '/tiendas-beds/<model("res.country.state"):state>',
    ], type='http', auth="public", website=True)
    def tiendas(self, state=None, **kw):
        cr, uid, context = request.cr, request.uid, request.context
        State = request.registry['res.country.state']
        if state:
            state = State.search(cr, SUPERUSER_ID, [('id','=', int(state))], context=context, limit=1)
            state = State.browse(cr, SUPERUSER_ID, state[0], context=context)
            if not state.country_state_beds:
                return request.redirect('/tiendas-beds', code=301)

        Partner = request.registry['res.partner']
        domain = [('beds_shop', '=', True),('partner_latitude','!=',0),('website_published','=',True),('beds_shop_closed','!=',True)]

        partner_ids = Partner.search(cr, SUPERUSER_ID, domain, context=context)

        # browse and format data
        partner_data = {
            "counter": len(partner_ids),
            "partners": []
        }


        keep = QueryURL('/tiendas-beds')

        request.context.update({'show_address': True})

        for partner in Partner.browse(cr, SUPERUSER_ID, partner_ids, context=context):

            # Calcular los horarios
            schedule1,schedule2,schedule3,schedule4 = self.schedule(partner)

            partner_data["partners"].append({
                'id': partner.id,
                'name': escape(partner.name),
                'latitude': escape(partner.partner_latitude),
                'longitude': escape(partner.partner_longitude),
                'street': escape(partner.street),
                'city': escape(partner.city),
                'zip': escape(partner.zip),
                'state': escape(partner.state_id.name),
                'phone': escape(partner.phone),
                'email': escape(partner.email),
                'nearest' : 0,
                'img' : escape("/website/image/res.partner/" + str(partner.id) + "/image" if partner.image else "/beds_theme/static/src/img/icon/logo1.png"),
                'schedule1' : escape(schedule1),
                'schedule2' : escape(schedule2),
                'schedule3' : escape(schedule3),
                'schedule4' : escape(schedule4),

            })

        # Buscar todas las provincias.
        domain = [('beds_shop', '=', True),('website_published','=',True),('beds_shop_closed','!=',True)]
        if state:
            domain += [('state_id','=',state.id)]

        partner_ids = Partner.search(cr, SUPERUSER_ID, domain, context=context)
        partner_ids = Partner.browse(cr, SUPERUSER_ID, partner_ids, context=context)

        domain = [('country_state_beds', '=', True)]
        states = State.search(cr, SUPERUSER_ID, domain, context=context, order='name asc')
        states = State.browse(cr, SUPERUSER_ID, states, context=context)

        Country = request.registry['res.country']
        domain = [('country_beds', '=', True)]
        countries = Country.search(cr, SUPERUSER_ID, domain, context=context, order='name desc')
        countries = Country.browse(cr, SUPERUSER_ID, countries, context=context)

        values = {
            'partner_data': json.dumps(partner_data),
            'keep' : keep,
            'category' : None,
            'countries' : countries,
            'state' : state,
            'states' : states,
            'shops' : partner_ids,
        }

        if state:
            values.update({
                'main_object' : state,
            })

        return request.website.render("beds_tiendas.tiendas", values)

    @http.route(['/tiendas-beds/<state>/<model("res.partner"):partner>',
    ], type='http', auth="public", website=True)
    def tienda_detail(self, state=None, partner=None, **kw):
        cr, uid, context = request.cr, request.uid, request.context

        """
        Partner = request.registry['res.partner']
        domain = [('id','=',partner.id),('beds_shop', '=', True)]
        partner = Partner.search(cr, SUPERUSER_ID, domain, context=context)
        partner = Partner.browse(cr, SUPERUSER_ID, partner, context=context)
        """

        if (not partner) or (not partner.beds_shop) or (not partner.website_published) or (partner.beds_shop_closed):
            if (partner.beds_shop) and (not partner.replace_by):
                return request.redirect("/tiendas-beds/%s" % slug(partner.state_id), code=302)
            elif (partner.beds_shop):
                return request.redirect('/tiendas-beds/' + partner.replace_by.state_id.name.replace(' ','-') + '/%s' % slug(partner.replace_by), code=302)

            return request.redirect("/tiendas-beds", code=301)

        keep = QueryURL('/tiendas-beds')

        schedule1,schedule2,schedule3,schedule4 = self.schedule(partner)

        values = {
            'main_object' : partner,
            'partner': partner,
            'keep' : keep,
            'schedule1' : escape(schedule1),
            'schedule2' : escape(schedule2),
            'schedule3' : escape(schedule3),
            'schedule4' : escape(schedule4),

        }

        return request.website.render("beds_tiendas.tienda", values)

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

    @http.route(['/form/contacto_tiendas',], type='http', auth="public", website=True)
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

        values["partner_id"] = kwargs.get("partner_id")
        _BEDSONLINE = ['-', ' ', '', None] # opciones que van directas a enviar a bedsonline@tiendasbeds.es
        email_tienda = kwargs.get("partner_email")
        if email_tienda not in _BEDSONLINE:
            values["email_cc"] = email_tienda
        else:
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
        template_id = template_obj.search(cr,SUPERUSER_ID,[('name','=','Formulario de tiendas')])

        if template_id:
            #_logger.debug("TEMPLATE FOUND")
            template_obj.send_mail(cr, SUPERUSER_ID, template_id[0], lead_id,context=context)
        return True
