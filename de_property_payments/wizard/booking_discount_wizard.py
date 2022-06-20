
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class BookingDiscountWizard(models.TransientModel):
    _name = "booking.discount.wizard"
    _description = "Booking Discount Wizard"
    

    discount = fields.Float(string='Disc(%)')
    installment_created = fields.Boolean(string='Installment Created')
    sale_id = fields.Many2one('sale.order', string='Order')
    plot_ids = fields.Many2many('sale.order.line', string='Plots')
    
    
    
    def action_book_discount(self):
        if self.discount < 0:
            raise UserError('You are not allow to Enter Discount less than Zero!')
        
        if self.sale_id.installment_created==True:
            disc = (self.sale_id.amount_total/100)  * self.discount
            tot_pending_count = 0
            for insta_line in self.sale_id.installment_line_ids:
                if insta_line.remarks=='Pending':
                    tot_pending_count += 1    
            for installment_line in self.sale_id.installment_line_ids:
                if self.discount ==0:
                    if insta_line.remarks=='Pending':
                        installment_line.update({
                            'amount_residual': installment_line.total_actual_amount - installment_line.amount_paid,
                            'total_amount': installment_line.total_actual_amount,
                        })
                else:  
                    installment_line.update({
                        'amount_residual': installment_line.total_actual_amount - installment_line.amount_paid,
                        'total_amount': installment_line.total_actual_amount,
                    })
                    if insta_line.remarks=='Pending':
                        if (disc/tot_pending_count) < installment_line.amount_residual:
                            installment_line.update({
                                'amount_residual': installment_line.amount_residual - (disc/tot_pending_count),
                                'total_amount': installment_line.total_actual_amount - (disc/tot_pending_count),
                            })
                
        else:
            for line in self.plot_ids:
                line.update({
                    'discount':  self.discount,
                })
        self.sale_id.update({
            'disc': self.discount,
        })    