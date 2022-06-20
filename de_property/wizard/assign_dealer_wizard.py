
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import date, datetime, timedelta


class AssignDealerWizard(models.TransientModel):
    _name = "assign.dealer.wizard"
    _description = "Assign Dealer wizard"
    

    partner_id = fields.Many2one('res.partner', string='Dealer/Customer')
    product_ids = fields.Many2many('product.product', string='Plot')
    date_reservation = fields.Date(string='Date of Reservation', required=True, default=fields.date.today())
    booking_validity = fields.Date(string='Booking Validity', required=True, default=fields.date.today()+timedelta(4))
    date_validity = fields.Date(string='Date Validity', required=True, default=fields.date.today()+timedelta(30))
    
    
    
    def action_assign_partner(self):
        for line in self.product_ids:
            line.update({
                'partner_id': self.partner_id.id,
                'cnic': self.partner_id.nic,
                'state': 'unconfirm',
                'date_validity': self.date_validity ,
                'booking_validity': self.booking_validity,
                'date_reservation': self.date_reservation ,
            })
        
        