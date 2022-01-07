
from odoo import models, SUPERUSER_ID, fields, api, _
import requests
import json

from odoo.http import request
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo import registry as registry_get

from odoo.addons import base


class GoogleMybusinessShopApi(models.TransientModel):
    _name = 'google.mybusiness.shop.api'

    def _get_default_partners(self):
        return self.env['res.partner'].browse(self.env.context.get('partner_id'))

    partner_ids = fields.Many2many(
        string="Shop",
        comodel_name="res.partner")
    access_token_api = fields.Char(
        string="Token")

    @api.multi
    def get_reviews_data(self):
        for records in self:
            for record in records.partner_ids:
                self.delete_previusly_reviews(record)
                self.get_api_reviews_data(record)

    def delete_previusly_reviews(self, accessInfo):

        Reviews_to_delete = self.env['res.partner.review_content']
        record_to_delete = Reviews_to_delete.search(
            [('partner_id', '=', accessInfo.id)])
        record_to_delete.sudo().unlink()

    def get_api_reviews_data(self, accessInfo):

        token = self.access_token_api

        url = 'https://mybusiness.googleapis.com/v4/' + \
            accessInfo.google_location + '/reviews?access_token=' + token

        payload = {}
        headers = {}

        response = requests.request(
            "GET", url, headers=headers, data=payload)

        data = response.json()
        continuar = True
        while continuar:
            if response.json().get('reviews'):
                for reviews in data['reviews']:
                    if reviews.get('starRating') == 'ONE':
                        star_rating = 1
                    elif reviews.get('starRating') == 'TWO':
                        star_rating = 2
                    elif reviews.get('starRating') == 'THREE':
                        star_rating = 3
                    elif reviews.get('starRating') == 'FOUR':
                        star_rating = 4
                    elif reviews.get('starRating') == 'FIVE':
                        star_rating = 5
                    else:
                        star_rating = 0

                    if reviews.get('comment'):
                        review_comment = reviews.get('comment')
                    else:
                        review_comment = None

                    if reviews.get('reviewReply'):
                        reply_comment = reviews['reviewReply']['comment'],
                        reply_update_time = reviews['reviewReply']['updateTime']
                    else:
                        reply_comment = None
                        reply_update_time = None

                    review_data = {
                        'partner_id': accessInfo.id,
                        'review_identificator': reviews.get('reviewId'),
                        'reviewer_profile_photo': reviews['reviewer']['profilePhotoUrl'],
                        'reviewer_displayname': reviews['reviewer']['displayName'],
                        'review_rating': star_rating,
                        'review_comment': review_comment,
                        'review_create_time': reviews.get('createTime'),
                        'review_update_time': reviews.get('updateTime'),
                        'reply_comment': reply_comment,
                        'reply_update_time': reply_update_time
                    }
                    review_create = self.env['res.partner.review_content'].sudo().create(
                        review_data)

            if response.json().get('nextPageToken'):
                url = 'https://mybusiness.googleapis.com/v4/' + \
                    accessInfo.google_location + '/reviews?access_token=' + \
                    token + '&pageToken=' + response.json().get('nextPageToken')

                response = requests.request(
                    "GET", url, headers=headers, data=payload)

                data = response.json()
            else:
                continuar = False

        return response
