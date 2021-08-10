# -*- coding: utf-8 -*-

import os
import openerp
from openerp.osv import orm, osv, fields
from openerp.tools import html_escape as escape, ustr, image_resize_and_sharpen, image_save_for_web
from openerp.tools.safe_eval import safe_eval
from openerp.addons.web.http import request
from openerp.http import request


import logging
_logger = logging.getLogger(__name__)


import hashlib



class website(osv.osv):
    _inherit = "website"


    def get_location(self, cr, uid, ids, arg=None, context=None):

        remote_ip = request.httprequest.remote_addr

        return remote_ip
