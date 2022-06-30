# -*- coding: utf-8 -*-

from odoo import models, fields, api, _ 


class AccountAsset(models.Model):
    _inherit = 'account.asset'
    
    
    specification = fields.Html(string='Specification')
    justification = fields.Html(string='Justification')
    location = fields.Char(string='Location')
    
    
