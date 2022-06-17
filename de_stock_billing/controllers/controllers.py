# -*- coding: utf-8 -*-
# from odoo import http


# class DeStockBilling(http.Controller):
#     @http.route('/de_stock_billing/de_stock_billing/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_stock_billing/de_stock_billing/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_stock_billing.listing', {
#             'root': '/de_stock_billing/de_stock_billing',
#             'objects': http.request.env['de_stock_billing.de_stock_billing'].search([]),
#         })

#     @http.route('/de_stock_billing/de_stock_billing/objects/<model("de_stock_billing.de_stock_billing"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_stock_billing.object', {
#             'object': obj
#         })
