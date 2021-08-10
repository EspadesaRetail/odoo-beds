# -*- coding: utf-8 -*-
from openerp import api, fields, models, _

import logging
_logger = logging.getLogger(__name__)

class CSBanner(models.Model):
    _name = "cs.carousel"
    _description = "Carousel"
    _order = 'name'

    name = fields.Char(string='Nombre', required=True)
    code = fields.Char(string='Código', required=True)

    # Timeline
    datetime_start = fields.Datetime('Inicio', required=True, help="Fecha y hora de inicio")
    datetime_end = fields.Datetime('Fin', required=True, help="Fecha y hora final")


    #localización
    all_area =  fields.Boolean('Global', default=False, copy=False, help="Indica si se utiliza en toda la web, independientemente de la zona localizada.")
    included_area = fields.Char('Área incluída', copy=False, help="Indica los códigos de provincia (01/50), donde aparecerá el banner."  )
    excluded_area = fields.Char('Área excluída', copy=False, help="Indica los códigos de provincia (01/50), donde NO aparecerá el banner."  )

    #Slides
    slide_ids = fields.Many2many('cs.carousel.slide', 'cs_carousel_slide_rel', 'carousel_id', 'slide_id', string='Slides', copy=True)

class CSBannerSlide(models.Model):
    _name = "cs.carousel.slide"
    _description = "Carousel slide"
    _order = 'sequence, name'

    name = fields.Char(string='Nombre')
    carousel_id = fields.Many2one('cs.carousel', string='Carousel')
    sequence = fields.Integer('Sequence', required=True, default = 1)

    link_url = fields.Char("Enlace")

    image_left_id = fields.Binary(string="Imágen izquierda", attachment=True, )
    image_right_id = fields.Binary(string="Imágen derecha", attachment=True, )

    en_image_left_id = fields.Binary(string="Left image", attachment=True,)
    en_image_right_id = fields.Binary(string="Right image", attachment=True)

    background = fields.Binary(string="Fondo", attachment=True)
    video = fields.Char("Vídeo")
    en_video = fields.Char("English video")


    @api.one
    def _url_image(self):
        self.url_image_left = '/website/image/cs.carousel.slide/%d/image_left_id' % self.id
        self.url_image_right =  '/website/image/cs.carousel.slide/%d/image_right_id' % self.id
        self.url_en_image_left = '/website/image/cs.carousel.slide/%d/en_image_left_id' % self.id
        self.url_en_image_right =  '/website/image/cs.carousel.slide/%d/en_image_right_id' % self.id

    url_image_left = fields.Char(compute='_url_image', string="Attachment left URL")
    url_image_right = fields.Char(compute='_url_image', string="Attachment right URL")
    url_en_image_left = fields.Char(compute='_url_image', string="Attachment left URL")
    url_en_image_right = fields.Char(compute='_url_image', string="Attachment right URL")
