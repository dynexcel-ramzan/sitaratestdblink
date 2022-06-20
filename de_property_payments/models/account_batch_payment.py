# -*- coding: utf-8 -*-
from odoo import models, fields, api, _




class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'
    
    order_id = fields.Many2one('sale.order', string='Order')
    partner_id = fields.Many2one('res.partner', string='Partner')
    narration  = fields.Char(string='Narration') 
    check_number = fields.Char(string='Check Number')
    
    
    def unlink(self):
        for pay in self.payment_ids:
            pay.action_cancel()
        res = super(AccountBatchPayment,self).unlink()
        
        return res
    
    
    
    
