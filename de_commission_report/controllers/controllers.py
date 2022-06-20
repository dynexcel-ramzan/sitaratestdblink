# -*- coding: utf-8 -*-
# from odoo import http


# class DeCommissionReport(http.Controller):
#     @http.route('/de_commission_report/de_commission_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_commission_report/de_commission_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_commission_report.listing', {
#             'root': '/de_commission_report/de_commission_report',
#             'objects': http.request.env['de_commission_report.de_commission_report'].search([]),
#         })

#     @http.route('/de_commission_report/de_commission_report/objects/<model("de_commission_report.de_commission_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_commission_report.object', {
#             'object': obj
#         })
