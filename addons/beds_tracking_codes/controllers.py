# -*- coding: utf-8 -*-
from openerp import http

# class BedsTrackingCodes(http.Controller):
#     @http.route('/beds_tracking_codes/beds_tracking_codes/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/beds_tracking_codes/beds_tracking_codes/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('beds_tracking_codes.listing', {
#             'root': '/beds_tracking_codes/beds_tracking_codes',
#             'objects': http.request.env['beds_tracking_codes.beds_tracking_codes'].search([]),
#         })

#     @http.route('/beds_tracking_codes/beds_tracking_codes/objects/<model("beds_tracking_codes.beds_tracking_codes"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('beds_tracking_codes.object', {
#             'object': obj
#         })