# -*- coding: utf-8 -*-
# from odoo import http


# class DeLedgerSaleReport(http.Controller):
#     @http.route('/de_ledger_sale_report/de_ledger_sale_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_ledger_sale_report/de_ledger_sale_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_ledger_sale_report.listing', {
#             'root': '/de_ledger_sale_report/de_ledger_sale_report',
#             'objects': http.request.env['de_ledger_sale_report.de_ledger_sale_report'].search([]),
#         })

#     @http.route('/de_ledger_sale_report/de_ledger_sale_report/objects/<model("de_ledger_sale_report.de_ledger_sale_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_ledger_sale_report.object', {
#             'object': obj
#         })
