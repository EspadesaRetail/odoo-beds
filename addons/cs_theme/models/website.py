# -*- coding: utf-8 -*-
from openerp import api, fields, models, _
from openerp.http import request
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime

import logging
_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    @api.model
    def get_carousel(self, code):
        zip_code = request.session.get('zip_code', False)
        now = datetime.now()

        domain=[('code','=',code)]
        domain += [('datetime_start', '<=', now.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]
        domain += [('datetime_end', '>=', now.strftime(DEFAULT_SERVER_DATETIME_FORMAT))]


        # Si no hay una localización establecida, se aplican sólo carruseles globales.
        if not zip_code:
            domain += [('all_area','=',True)]
            _logger.debug("Search carousel by code <%s> and all areas." % code)

        # Si hay una localización, se aplica, en función de si un área está incluída o excluída.
        else:
            area = zip_code[:2]
            domain += ['|',('included_area','ilike',area), ('excluded_area','not ilike',area)]
            _logger.debug("Search carousel by code:[%s] and area:<%s> " % (code, str(area)))

        Carousel = self.env['cs.carousel']
        carousel_id = Carousel.search(domain)
        if not carousel_id:
            _logger.debug("The carousel <%s> is not defined." % code)
            return None

        return carousel_id[0]
