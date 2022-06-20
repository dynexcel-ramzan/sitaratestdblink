
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, timedelta

class generate_booking_wizard(models.TransientModel):
    _name = "generate.booking.wizard"
    _description = "Generate Booking Wizard"
    

    partner_id = fields.Many2one('res.partner', string='Dealer/Customer')
    commission_type = fields.Selection([
        ('amount', 'Amount'),
        ('percent', 'Percentage'),
        ], string='Commission Type', default='amount') 
    
    commision_amount = fields.Float(string='Commission')
    discount = fields.Float(string='Disc%')
    product_ids = fields.Many2many('product.product', string='Plot')
    date_reservation = fields.Date(string='Booking Date', required=True, default=fields.date.today() )
    date_validity = fields.Date(string='Date Validity', required=True, default=fields.date.today()+timedelta(30))
    
    
    
    
    def action_assign_partner(self):
        for line in self.product_ids:
            if line.state=='available':
                line.update({
                   'date_reservation': self.date_reservation,
                })
            line.update({
                'partner_id': self.partner_id.id,
                'cnic': self.partner_id.nic,
                'state': 'reserved',
                'booking_validity': self.date_reservation,
                'date_validity': self.date_validity,
            })
        booking_vals = {
            'partner_id': self.partner_id.id,
            'date_order': self.date_reservation,
        }
        booking = self.env['sale.order'].create(booking_vals)
        for prd_line in self.product_ids:
            prd_line.update({
                'booking_id': booking.id,
            })
            total_commision_amount = self.commision_amount
            if self.commission_type=='percent':
                total_commision_amount = (prd_line.list_price/100)*self.commision_amount
            line_vals = {
                'order_id': booking.id,
                'product_id': prd_line.id,
                'price_unit':  prd_line.list_price,
                'comission_amount': total_commision_amount,
                'discount': self.discount,
            }
            booking_line = self.env['sale.order.line'].create(line_vals)
        