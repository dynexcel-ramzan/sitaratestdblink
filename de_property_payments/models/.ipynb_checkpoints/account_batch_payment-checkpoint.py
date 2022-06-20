# -*- coding: utf-8 -*-
from odoo import models, fields, api, _




class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'
    
    order_id = fields.Many2one('sale.order', string='Order')
    
    def unlink(self):
        for pay in self.payment_ids:
            pay.action_cancel()
        res = super(AccountBatchPayment,self).unlink()
        
        return res
    
    
    
    
