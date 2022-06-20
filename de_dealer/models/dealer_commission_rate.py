# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleDealerCommissionRate(models.Model):
    _name = 'sale.dealer.commission.rate'
    _description="sale dealer commission rate"

    commission_rate = fields.Float(string='Commission Rate (%)', digits='Discount', default=0.0, required=True)
    dealer_id = fields.Many2one('res.partner', domain="[('is_dealer','=', True)]", string="Dealer", required=True,)
    
    
        