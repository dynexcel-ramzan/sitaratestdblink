
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
from odoo.exceptions import UserError


class UniqPlotResellWizard(models.TransientModel):
    _name = "uniq.plot.resell.wizard"
    _description = "Uniq Plot Resell wizard"
    

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    reseller_id = fields.Many2one('res.partner', string='Reseller')
    resell_date = fields.Date(string='Reselling Date',  required=True, default=fields.date.today())
    product_ids = fields.Many2many('product.product', string='Products')

    def action_confirm(self):
        payment_list=[]
        for line in self.product_ids:
            resell_vals={
                'partner_id': self.reseller_id.id,
                'customer_id': self.partner_id.id,
                'date': self.resell_date,
                'product_id': line.product_tmpl_id.id,
                'amount_paid': line.amount_paid,
                'amount_residual': line.amount_residual,
            }
            reseller = self.env['uniq.reseller.line'].create(resell_vals)
            line.update({
                'partner_id': self.partner_id.id,
            }) 
            for pay in line.payment_ids:
                payment_list.append(pay.id)
                
            for booking_line  in  line.booking_id.order_line:
                if booking_line.product_id.id==line.id:
                   booking_line.unlink() 
        booking_vals = {
            'partner_id': self.partner_id.id,
            'date_order': self.resell_date,
        }
        booking = self.env['sale.order'].create(booking_vals)
        for prd_line in self.product_ids:
            fee_payment=self.env['account.payment'].search([('order_id','=',prd_line.booking_id.id),('plot_id','=',prd_line.id),('processing_fee_submit','=',True),('amount','=',prd_line.categ_id.process_fee)] ,limit=1)
            fee_payment.update({
               'order_id':booking.id,
               'partner_id':self.partner_id.id,
            })
            membership_fee_payment=self.env['account.payment'].search([('order_id','=',prd_line.booking_id.id),('plot_id','=',prd_line.id),('membership_fee_submit','=', True),('amount','=',prd_line.categ_id.allottment_fee)] ,limit=1)
            membership_fee_payment.update({
               'order_id':booking.id,
            })
            if fee_payment:
                booking.update({
                    'processing_fee_submit':True,
                })
            prd_line.update({
                'booking_id': booking.id,
            })
            
            line_vals = {
                'order_id': booking.id,
                'product_id': prd_line.id,
                'price_unit':  prd_line.list_price,
            }
            booking_line = self.env['sale.order.line'].create(line_vals)             
        payments=self.env['account.payment'].search([('id','in', payment_list)])        
        batch_journal_list = []
        batch_list = []
        for pay_line in payments: 
            batch_journal_list.append(pay_line.journal_id.id)
            batch_list.append(pay_line.batch_payment_id.id)
            pay_line.action_draft()
            pay_line.update({
                'partner_id': self.partner_id.id,
                'order_id': booking.id,
            })
            pay_line.action_post()
            pay_line.batch_payment_id.update({
                    'state': 'reconciled',
                })
            
        batch_journal_list.append(fee_payment.journal_id.id) 
        payment_list.append(fee_payment.id)
        batch_journal_list.append(membership_fee_payment.journal_id.id)
        payment_list.append(membership_fee_payment.id)
        uniq_batch_journal_list = set(batch_journal_list)
        unique_batch_list = set(batch_list)
        for uniq_batch in uniq_batch_journal_list:
            if uniq_batch!=False:
                total_b_pay = 0
                final_payment_list = []
                batch_pay = self.env['account.payment'].search([('id','in', payment_list),('journal_id','=',uniq_batch)])
                for b_pay in batch_pay:
                    final_payment_list.append(b_pay.id)
                    total_b_pay += b_pay.amount    
                batch_vals = {
                    'batch_type': 'inbound',
                    'journal_id': uniq_batch,
                    'partner_id':  self.partner_id.id,
                    'narration':  ' Customer Payments '+ str(total_b_pay) +' - '+ str(self.partner_id.name),  
                    'order_id': booking.id,
                    'date': fields.date.today(),
                    'state': 'reconciled',
                } 
                batch=self.env['account.batch.payment'].create(batch_vals)
                batch.update({
                    'state': 'reconciled',
                })
                batch.payment_ids=final_payment_list
                batch.update({
                   'state': 'reconciled',
                })
                
        for unique_batch in unique_batch_list:
            batch_paym=self.env['account.batch.payment'].search([('id','=', unique_batch)])
            batch_paym.update({
                   'state': 'reconciled',
                })
            
            