# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleDealerCommissionLine(models.Model):
    _name = 'sale.dealer.commission.line'
    _description = "sale dealer commission line"

#     status will also be included

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.dealer.commission.line')
        result = super(SaleDealerCommissionLine, self).create(vals)
        return result
    name = fields.Char('Name', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    
    sale_id = fields.Many2one('sale.order', string="Sale", domain="[('state', '=', 'done')]" )
    date_order = fields.Datetime(related='sale_id.date_order')
    product_id = fields.Many2one('product.product', compute='_compute_sale_product')
    
    partner_id = fields.Many2one(related='sale_id.partner_id', string="Customer", store=True)
    dealer_id = fields.Many2one(related='sale_id.dealer_id', string="Dealer", store=True)
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount_received = fields.Monetary(related='sale_id.amount_received', string="Amount Received")
    amount_total = fields.Monetary(related='sale_id.amount_total', string="Total Amount", store=True)
    state = fields.Selection(related='sale_id.state', string="State")
    @api.depends('comission_rate','dealer_id')
    def _get_coon_rate(self):
        for line in self:
            record = self.env['sale.dealer.commission.rate'].search([('dealer_id','=',line.dealer_id.id)])
            line.update({
                            'comission_rate': record.commission_rate
                        })      
    comission_rate = fields.Float( compute='_get_coon_rate', string="Comission Rate", store=True)

    @api.depends('sale_id')
    def _compute_sale_product(self):
        for com in self:
            product_id = False
            for line in com.sale_id.order_line:
                if line.product_id:
                    product_id = line.product_id.id
            com.product_id = product_id
    @api.depends('commision_amount', 'amount_total', 'comission_rate')
    def _get_commission_amount(self):
        for line in self:
            line.update({
                            'commision_amount': line.comission_rate * line.amount_total
                        })   
    commision_amount = fields.Float( compute='_get_commission_amount', string="Comission Amount", store=True)
    

    def create_invoice_action(self):
        product_list = []
        for line in self:
            product_list.append((0,0, {
                    'name': line.name,
#                     'account_id': line.account_id.id,
                    'quantity': 1,
                    'price_unit': line.commision_amount,
                    'partner_id': line.dealer_id.id,
                        }))     
            
            vals = {
                    'partner_id': line.partner_id.id,
                    'journal_id': 3,
                    'invoice_date': fields.Date.today(),
                    'move_type': 'out_invoice',
                    'invoice_origin': line.sale_id.name,
                    'invoice_line_ids': product_list ,  
                    }
            move = self.env['account.move'].create(vals)   
