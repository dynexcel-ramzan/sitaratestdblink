# -*- coding: utf-8 -*-
# from odoo import http


# class DePropertyReport(http.Controller):
#     @http.route('/de_property_report/de_property_report', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_property_report/de_property_report/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_property_report.listing', {
#             'root': '/de_property_report/de_property_report',
#             'objects': http.request.env['de_property_report.de_property_report'].search([]),
#         })

#     @http.route('/de_property_report/de_property_report/objects/<model("de_property_report.de_property_report"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_property_report.object', {
#             'object': obj
#         })
