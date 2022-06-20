# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrder(models.Model):
    _inherit = 'sale.order'

#     dealers = fields.Many2many (related='team_id.dealer_id')
    dealer_id = fields.Many2one('res.partner', domain="[('active_dealer', '=', True)]", string="Dealer",)
    amount_received = fields.Monetary('Amount Received')
    plot_name = fields.Char('Plot', compute='compute_plot_name')
    
    def compute_plot_name(self):
        
        for rec in self:
            val = ''
            if rec.order_line:
                for line in rec.order_line:
                    val = val + str(line.product_id.name)+'/'
                rec.plot_name = val[:-1]
            else:
                rec.plot_name = val
    
    def action_confirm(self):
        rec = super(SaleOrder, self).action_confirm()
        vals = {
            'sale_id':self.id,        
        }
        self.env['sale.dealer.commission.line'].create(vals)
        return rec
    
    
    
    