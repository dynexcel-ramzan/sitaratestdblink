# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    process_fee = fields.Float(string='Processing Fee')
    allottment_fee = fields.Float(string='Membership Fee')
    
    
    
    
