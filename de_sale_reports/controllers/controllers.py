# -*- coding: utf-8 -*-
# from odoo import http


# class DeSaleReports(http.Controller):
#     @http.route('/de_sale_reports/de_sale_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_sale_reports/de_sale_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_sale_reports.listing', {
#             'root': '/de_sale_reports/de_sale_reports',
#             'objects': http.request.env['de_sale_reports.de_sale_reports'].search([]),
#         })

#     @http.route('/de_sale_reports/de_sale_reports/objects/<model("de_sale_reports.de_sale_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_sale_reports.object', {
#             'object': obj
#         })
