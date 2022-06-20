# -*- coding: utf-8 -*-
# from odoo import http


# class DeOpenders(http.Controller):
#     @http.route('/de_openders/de_openders/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_openders/de_openders/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_openders.listing', {
#             'root': '/de_openders/de_openders',
#             'objects': http.request.env['de_openders.de_openders'].search([]),
#         })

#     @http.route('/de_openders/de_openders/objects/<model("de_openders.de_openders"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_openders.object', {
#             'object': obj
#         })
