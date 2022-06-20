# -*- coding: utf-8 -*-
# from odoo import http


# class DeAccountReports(http.Controller):
#     @http.route('/de_account_reports/de_account_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_reports/de_account_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_reports.listing', {
#             'root': '/de_account_reports/de_account_reports',
#             'objects': http.request.env['de_account_reports.de_account_reports'].search([]),
#         })

#     @http.route('/de_account_reports/de_account_reports/objects/<model("de_account_reports.de_account_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_reports.object', {
#             'object': obj
#         })
