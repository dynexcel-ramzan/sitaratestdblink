# -*- coding: utf-8 -*-
# from odoo import http


# class DePropertyPayments(http.Controller):
#     @http.route('/de_property_payments/de_property_payments', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_property_payments/de_property_payments/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_property_payments.listing', {
#             'root': '/de_property_payments/de_property_payments',
#             'objects': http.request.env['de_property_payments.de_property_payments'].search([]),
#         })

#     @http.route('/de_property_payments/de_property_payments/objects/<model("de_property_payments.de_property_payments"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_property_payments.object', {
#             'object': obj
#         })
