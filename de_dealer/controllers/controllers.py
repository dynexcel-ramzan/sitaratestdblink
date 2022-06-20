# -*- coding: utf-8 -*-
# from odoo import http


# class DeDealer(http.Controller):
#     @http.route('/de_dealer/de_dealer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_dealer/de_dealer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_dealer.listing', {
#             'root': '/de_dealer/de_dealer',
#             'objects': http.request.env['de_dealer.de_dealer'].search([]),
#         })

#     @http.route('/de_dealer/de_dealer/objects/<model("de_dealer.de_dealer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_dealer.object', {
#             'object': obj
#         })
