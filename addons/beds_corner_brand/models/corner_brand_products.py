# -*- coding: utf-8 -*-

from openerp import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)


class corner_brand_products(models.Model):
    _name = 'corner.brand.products'
    _description = 'Products for Brand microsites'

    name = fields.Char(string='Name',
                       translate=True,
                       help="This field is used as heading of product card")
    title = fields.Char(string='Title',
                        translate=True,
                        help="This field is used to add more info about product card")
    image = fields.Binary("Image",
                          help="This field holds the image used as image for product card, limited to 1024x1024px.")
    youtube_link_large = fields.Char(string='Link to large video from Youtube',
                                     translate=True,
                                     help="Youtube video, this one occupy the entire width of card")
    youtube_link_small = fields.Char(string='Link to small video from Youtube',
                                     translate=True,
                                     help="Youtube video, this one occupy only a half width of card")
    free_text_small_title = fields.Char(string='Title for Small Free Text', translate=True)
    free_text_small = fields.Text(string='Small Free Text', translate=True)
    free_text_large_title = fields.Char(string='Title for Large Free Text', translate=True)
    free_text_large = fields.Text(string='Large Free Text', translate=True)
    corner_brand_id = fields.Many2one(comodel_name='corner.brand', string='Brand', translate=True)
    product_id = fields.Many2one(comodel_name='product.template', sting='Product', translate=True)

    # Devolver la url de la imagen de la ficha.
    def _label_url(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, '')
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = self.pool.get('website').image_url(cr, uid, obj, 'image')
        return result
