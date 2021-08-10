# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import time
from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp import workflow
import logging
_logger = logging.getLogger(__name__)
