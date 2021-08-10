# -*- coding: utf-8 -*-


from openerp import api, tools
from openerp.osv import osv, fields, expression

import logging
import json
_logger = logging.getLogger(__name__)


class res_partner(osv.osv):
    """ Inherits partner and adds contract information in the partner form """
    _inherit = 'res.partner'

    _columns = {


        # Añadir datos relativos a las tiendas bed's
        'beds_shop': fields.boolean("Tienda Bed's", help="Check this box if this contact is a Bed's shopping."),

        'partner_google_localization': fields.text('Localización en Google Maps'),
        'partner_brochure_id': fields.many2one('res.partner_brochure', 'Folleto publicitario', domain=[('current_brochure','!=',False)]),

        'monday_schedule': fields.char("Horario lunes", copy=False),
        'weekly_schedule': fields.char("Horario semanal (L-V)", copy=False),
        'saturday_schedule': fields.char("Horario sábado", copy=False),
        'summer_schedule': fields.char("Horario de verano", copy=False),

        'beds_shop_closed': fields.boolean("Tienda Bed's cerrada", help="Check this box if this contact is a Bed's shopping closed."),
        'replace_by': fields.many2one('res.partner', 'Reemplazada por', help="This field indicates that Bed's shopping is replaced by another Bed's shopping.", domain=[('beds_shop','!=',False),('beds_shop_closed','=',False)]),

        'website_description': fields.html('Website Partner Full Description', strip_style=True, translate=True),
        'website_short_description': fields.text('Website Partner Short Description', translate=True),

    }

    _defaults = {
        'beds_shop_closed': False,
        'website_published': False
    }
