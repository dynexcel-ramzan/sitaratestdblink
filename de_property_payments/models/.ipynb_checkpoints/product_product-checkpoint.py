# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    def action_uniq_resell_plots(self):
        
        for rec in self:
            if rec.state in ('available','posted_sold'):
                raise UserError('Not Allow to Re-Sell Sold or Available Plot!')
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['product.product'].browse(selected_ids)
        return {
            'name': ('Plot Reselling'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'uniq.plot.resell.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_product_ids': selected_records.ids,'default_reseller_id': self.partner_id.id},
        }


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    reseller_ids = fields.One2many('uniq.reseller.line', 'product_id', string='Resellers')
    
    
    
    
class UniqPlotsReseller(models.Model):
    _name = 'uniq.reseller.line'
    _descrption='Uniq Reseller Lines'
    
    partner_id = fields.Many2one('res.partner', string='Reseller', required=True)
    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    date = fields.Date(string='Reselling Date', required=True)
    amount_paid = fields.Float(string='Amount Paid', required=True)
    amount_residual = fields.Float(string='Amount Due', required=True)
    product_id = fields.Many2one('product.template', string='Product')
        
    
    
