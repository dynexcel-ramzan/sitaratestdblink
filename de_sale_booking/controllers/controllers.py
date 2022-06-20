# -*- coding: utf-8 -*-
# from odoo import http


# class DSaleBooking(http.Controller):
#     @http.route('/d_sale_booking/d_sale_booking', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/d_sale_booking/d_sale_booking/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('d_sale_booking.listing', {
#             'root': '/d_sale_booking/d_sale_booking',
#             'objects': http.request.env['d_sale_booking.d_sale_booking'].search([]),
#         })

#     @http.route('/d_sale_booking/d_sale_booking/objects/<model("d_sale_booking.d_sale_booking"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('d_sale_booking.object', {
#             'object': obj
#         })
