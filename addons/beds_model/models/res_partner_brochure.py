# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class res_partner_brochure(models.Model):
    _name = 'res.partner_brochure'
    _description = 'Brochure embed code'

    name = fields.Char(string='Name',
                       translate=True,
                       help="This field is used to set a name")
    title = fields.Char(string='Title',
                        translate=True)
    brochure_url = fields.Char(string='URL',
                               translate=True,
                               help="This field is used to set the url")        
    partner_ids = fields.One2many(comodel_name='res.partner',
                                  inverse_name='partner_brochure_id',
                                  string='Selected Shops')
    current_brochure = fields.Boolean(string='Active',
                                      translate=True)
