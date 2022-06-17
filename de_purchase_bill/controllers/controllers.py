# -*- coding: utf-8 -*-
# from odoo import http


# class DePurchaseBill(http.Controller):
#     @http.route('/de_purchase_bill/de_purchase_bill/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_purchase_bill/de_purchase_bill/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_purchase_bill.listing', {
#             'root': '/de_purchase_bill/de_purchase_bill',
#             'objects': http.request.env['de_purchase_bill.de_purchase_bill'].search([]),
#         })

#     @http.route('/de_purchase_bill/de_purchase_bill/objects/<model("de_purchase_bill.de_purchase_bill"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_purchase_bill.object', {
#             'object': obj
#         })
