# -*- coding: utf-8 -*-
import openerp
from openerp.osv import orm, osv, fields

class website(osv.osv):
    _name = 'website'
    _inherit = 'website'
    _columns = {
        'google_tag_manager_key': fields.char('Google Tag Manager Key'),
    }

    
    
class website_config_settings(osv.osv_memory):
    _name = 'website.config.settings'
    _inherit = 'website.config.settings'

    _columns = {
        'google_tag_manager_key': fields.related('website_id', 'google_tag_manager_key', type="char", string='Google Tag Manager Key'),
    }

    