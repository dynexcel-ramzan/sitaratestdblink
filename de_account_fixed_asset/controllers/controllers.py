# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountFixedAsset(http.Controller):
#     @http.route('/de_account_fixed_asset/de_account_fixed_asset', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_fixed_asset/de_account_fixed_asset/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_fixed_asset.listing', {
#             'root': '/de_account_fixed_asset/de_account_fixed_asset',
#             'objects': http.request.env['de_account_fixed_asset.de_account_fixed_asset'].search([]),
#         })

#     @http.route('/de_account_fixed_asset/de_account_fixed_asset/objects/<model("de_account_fixed_asset.de_account_fixed_asset"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_fixed_asset.object', {
#             'object': obj
#         })
