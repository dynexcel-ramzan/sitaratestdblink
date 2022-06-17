# -*- coding: utf-8 -*-
# from odoo import http


# class DePurchaseBillAdv(http.Controller):
#     @http.route('/de_purchase_bill_adv/de_purchase_bill_adv/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_purchase_bill_adv/de_purchase_bill_adv/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_purchase_bill_adv.listing', {
#             'root': '/de_purchase_bill_adv/de_purchase_bill_adv',
#             'objects': http.request.env['de_purchase_bill_adv.de_purchase_bill_adv'].search([]),
#         })

#     @http.route('/de_purchase_bill_adv/de_purchase_bill_adv/objects/<model("de_purchase_bill_adv.de_purchase_bill_adv"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_purchase_bill_adv.object', {
#             'object': obj
#         })
