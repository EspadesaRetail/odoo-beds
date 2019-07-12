# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, SUPERUSER_ID, _


class SurveyChecklistQuestion(models.Model):
    _name = 'survey.question'
    _inherit = 'survey.question'
    _description = 'Survey Checklist Question addons'

    image_allowed = fields.Boolean('Show Image Field')

class SurveyChecklistUserInputLine(models.Model):

    _name = 'survey.user_input_line'
    _inherit = 'survey.user_input_line'
    _description = 'Survey Checklist UserInputLine addons'

    image = fields.Binary("Logo", attachment=True,
        help="This field holds the image used as logo for the brand, limited to 1024x1024px.")
    image_medium = fields.Binary("Medium-sized image", attachment=True,
        help="Medium-sized logo of the brand. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary("Small-sized image", attachment=True,
        help="Small-sized logo of the brand. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
