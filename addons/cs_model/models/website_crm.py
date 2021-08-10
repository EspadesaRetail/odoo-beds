# -*- coding: utf-8 -*-
from openerp import api
from openerp.tools.translate import _
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import datetime
from openerp import SUPERUSER_ID

import logging
import json
_logger = logging.getLogger(__name__)



"""
Definicion de todo lo necesario para gestionar la web en base a campañas.
"""
"""
class website_campaign_banner(osv.Model):
    # OLD crm.case.resource.type
    _name = "website.campaign.banner"
    _description = "Website Campaign banners"
    _columns = {
        'name': fields.char('Name', required=True, translate=True),
        'campaign_id': fields.many2one('website.campaign', 'Campaign'),
        'attachment_ids': fields.many2many('ir.attachment', 'website_campaign_banners_rel', 'campaign_banner_id',
                            'attachment_id', 'Campaign banners',help="You may attach files to this campaign for home banners"),
    }
"""

class website_campaign(osv.Model):
    # OLD crm.case.resource.type
    _name = "website.campaign"
    _description = "Website Campaign"
    _columns = {
        'name': fields.char('Campaign Name', required=True, translate=True),
        'active': fields.boolean('Active',
            help="When a version is duplicated it is set to non active, so that the " \
            "dates do not overlaps with original version. You should change the dates " \
            "and reactivate the pricelist"),
        'datetime_start': fields.datetime('Inicio', help="Fecha inicial campaña"),
        'datetime_end': fields.datetime('Fin', help="Fecha final campaña"),

        #'home_banner_ids': fields.one2many('website.campaign.banner', 'campaign_id', 'Home banners'),


    }
    _defaults = {
        'active': lambda *a: False,
    }

    # Comprueba que no existan dos campañas activas y colisionen en las fechas.
    def _check_datetime(self, cursor, user, ids, context=None):
        for o in self.browse(cursor, user, ids, context=context):




            if not o.active:
                continue

            where = []
            if o.datetime_start:
                where.append("((datetime_end>='%s') or (datetime_end is null))" % (o.datetime_start,))
            if o.datetime_end:
                where.append("((datetime_start<='%s') or (datetime_start is null))" % (o.datetime_end,))

            s = 'SELECT id FROM website_campaign ' \
                    'WHERE '+' and '.join(where) + (where and ' and ' or '')+ \
                        'active ' 'AND id <> %s' % str(o.id)

            _logger.debug("WHERE: " + str(s))

            cursor.execute(s)
            if cursor.fetchall():
                return False

        return True


    # Obtener la camapaña actual
    def get_current_campaign(self, cr, uid, context=None):
        # Current date time.
        dt = datetime.datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        _logger.debug("Get current campaign for datetime: %s" % dt)

        ids = self.search(cr, SUPERUSER_ID, [('datetime_start', '<=', dt),('datetime_end', '>=', dt), ('active' , '=', 'True')], context=context)
        if ids:
            return self.browse(cr,uid,ids[0])

        _logger.debug("No current campaign")
        return False



    _constraints = [
        (_check_datetime, 'You cannot have 2 campaigns versions that overlap!',
            ['datetime_start', 'datetime_end','active'])
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        # set active False to prevent overlapping active campaign
        # versions
        if not default:
            default = {}
        default['active'] = False
        return super(website_campaign, self).copy(cr, uid, id, default, context=context)
