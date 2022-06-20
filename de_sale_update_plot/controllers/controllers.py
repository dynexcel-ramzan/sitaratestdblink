# -*- coding: utf-8 -*-
# from odoo import http


# class DeSaleUpdatePlot(http.Controller):
#     @http.route('/de_sale_update_plot/de_sale_update_plot', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_sale_update_plot/de_sale_update_plot/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_sale_update_plot.listing', {
#             'root': '/de_sale_update_plot/de_sale_update_plot',
#             'objects': http.request.env['de_sale_update_plot.de_sale_update_plot'].search([]),
#         })

#     @http.route('/de_sale_update_plot/de_sale_update_plot/objects/<model("de_sale_update_plot.de_sale_update_plot"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_sale_update_plot.object', {
#             'object': obj
#         })
