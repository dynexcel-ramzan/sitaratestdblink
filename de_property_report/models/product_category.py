# # -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductCategory(models.Model):
    _inherit = 'product.category'
    
    can_be_property = fields.Boolean(string='Property Category')

