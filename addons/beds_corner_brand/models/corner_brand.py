# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class corner_brand(models.Model):
    _name = 'corner.brand'
    _description = 'Header for Brand microsites'

    name = fields.Char(string='Name',
                       translate=True,
                       help="This field is used to set the url")
    title = fields.Char(string='Title',
                        translate=True)
    subtitle = fields.Text(string='Add more info about brand',
                           translate=True)
    image = fields.Binary("Image",
                          help="This field holds the image used as image for brand, limited to 1024x1024px.")
    corner_brand_products_ids = fields.One2many(comodel_name='corner.brand.products',
                                                inverse_name='corner_brand_id',
                                                string='Selected Products')

    # Devolver la url de la imagen de la marca.
    def _label_url(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = self.pool.get('website').image_url(cr, uid, obj, 'image')
        return result
