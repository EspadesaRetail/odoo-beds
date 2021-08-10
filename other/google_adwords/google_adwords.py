# -*- coding: utf-8 -*-
import openerp
from openerp.osv import orm, osv, fields

class website(osv.osv):
    _name = 'website'
    _inherit = 'website'
    _columns = {
        'google_adwords_conversion_id': fields.char('Google Adwords Conversion Id'),
        'google_adwords_conversion_label': fields.char('Google Adwords Conversion Label'),
    }

    
    
class website_config_settings(osv.osv_memory):
    _name = 'website.config.settings'
    _inherit = 'website.config.settings'

    _columns = {
        'google_adwords_conversion_id': fields.related('website_id', 'google_adwords_conversion_id', type="char", string='Gooole Adwords Conversion Id'),
        'google_adwords_conversion_label': fields.related('website_id', 'google_adwords_conversion_label', type="char", string='Gooole Adwords Conversion Label'),
    }

    