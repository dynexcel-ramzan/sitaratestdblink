# -*- coding: utf-8 -*-
# from odoo import http


# class DePartnerTax(http.Controller):
#     @http.route('/de_partner_tax/de_partner_tax/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_partner_tax/de_partner_tax/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_partner_tax.listing', {
#             'root': '/de_partner_tax/de_partner_tax',
#             'objects': http.request.env['de_partner_tax.de_partner_tax'].search([]),
#         })

#     @http.route('/de_partner_tax/de_partner_tax/objects/<model("de_partner_tax.de_partner_tax"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_partner_tax.object', {
#             'object': obj
#         })
