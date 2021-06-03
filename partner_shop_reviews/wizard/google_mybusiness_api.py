
from odoo import models, SUPERUSER_ID, fields, api, _
import requests
import json

from odoo.http import request
from odoo.exceptions import AccessDenied, UserError
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo import registry as registry_get

from odoo.addons import base


class GoogleMybusinessApi(models.TransientModel):
    _name = 'google.mybusiness.api'

    def _get_default_partners(self):
        return self.env['res.partner'].browse(self.env.context.get('partner_id'))

    format_ids = fields.Many2many(
        string="Format",
        comodel_name="res.partner.format")
    access_token_api = fields.Char(
        string="Token")

    @api.multi
    def get_reviews(self):
        for records in self:
            for record in records.format_ids:
                self.get_api_locations(record)

    def get_api_accounts(self):

        token = self.access_token_api

        url = 'https://mybusiness.googleapis.com/v4/accounts/?access_token=' + token

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        print(response.text)

    def get_api_locations(self, accessInfo):

        token = self.access_token_api

        url = 'https://mybusiness.googleapis.com/v4/' + \
            accessInfo.google_account + '/locations/?access_token=' + token

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        data = response.json()
        continuar = True
        while continuar:
            for location in data['locations']:
                if location['storeCode'].isnumeric():
                    domain = [('espadesa_shop', '=', location['storeCode'])]
                    partner = self.format_id = self.env['res.partner'].sudo().search(
                        domain)
                    if partner:
                        partner.update({'google_location': location['name']})
                        self.get_api_reviews(partner)

            if response.json().get('nextPageToken'):
                url = 'https://mybusiness.googleapis.com/v4/' + \
                    accessInfo.google_account + '/locations/?access_token=' + \
                    token + '&pageToken=' + response.json().get('nextPageToken')

                response = requests.request(
                    "GET", url, headers=headers, data=payload)

                data = response.json()
            else:
                continuar = False

        return response

    def get_api_reviews(self, accessInfo):

        token = self.access_token_api

        url = 'https://mybusiness.googleapis.com/v4/' + \
            accessInfo.google_location + '/reviews?access_token=' + token

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        valor = {
            'partner_id': accessInfo.id,
            'review_number': response.json().get('totalReviewCount'),
            'review_value': response.json().get('averageRating')
        }
        if response.json().get('totalReviewCount') and response.json().get('averageRating'):
            review = self.env['res.partner.review'].sudo().create(valor)

        return response
