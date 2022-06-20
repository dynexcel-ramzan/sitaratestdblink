# -*- coding: utf-8 -*-
# from odoo import http


# class DePaymentRecieptReport(http.Controller):
#     @http.route('/de_payment_reciept_report/de_payment_reciept_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_payment_reciept_report/de_payment_reciept_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_payment_reciept_report.listing', {
#             'root': '/de_payment_reciept_report/de_payment_reciept_report',
#             'objects': http.request.env['de_payment_reciept_report.de_payment_reciept_report'].search([]),
#         })

#     @http.route('/de_payment_reciept_report/de_payment_reciept_report/objects/<model("de_payment_reciept_report.de_payment_reciept_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_payment_reciept_report.object', {
#             'object': obj
#         })
