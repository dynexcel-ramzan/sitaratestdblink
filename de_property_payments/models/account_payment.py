# -*- coding: utf-8 -*-
from odoo import models, fields, api, _




class AccountPayment(models.Model):
    _inherit = 'account.payment'
    
    order_id = fields.Many2one('sale.order', string='Order')
    plot_id = fields.Many2one('product.product', string='plot')
    processing_fee_submit = fields.Boolean(string='Processing Fee Submitted')
    membership_fee_submit = fields.Boolean(string='Membership Fee Submitted')
    installment_id = fields.Many2one('order.installment.line', string='Order Installment')
    remarks = fields.Char(string='Remarks')    
    type = fields.Selection([
        ('token','Token'),
        ('fee', 'Fee'),
        ('book', 'Booking'),
        ('allott', 'Allottment'),
        ('installment', 'Installment'),
        ], string='Type')
    
    
    def action_cancel(self):
        for line in self:
            if line.installment_id:
                diff=line.installment_id.amount_paid - line.amount
                line.installment_id.update({
                    'remarks': 'Pending',
                    'amount_paid': line.installment_id.amount_paid - line.amount,
                    'amount_residual':line.installment_id.amount_residual + line.amount,
                })
            if line.order_id.amount_paid==0:
               line.order_id.update({
                   'state': 'draft'
               }) 
            if line.type=='fee':
                if line.processing_fee_submit== True:
                    line.order_id.update({
                       'processing_fee_submit': False
                    }) 
            if line.membership_fee_submit== True:
                    line.order_id.update({
                       'membership_fee_submit': False
                    }) 
            res = super(AccountPayment, line).action_cancel()
            return  res
    
    
    
