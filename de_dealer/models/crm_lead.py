# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class crmLead(models.Model):
    _inherit = 'crm.lead'
    
    dealers = fields.Many2many (related='team_id.dealer_id')
    dealer_id = fields.Many2one('res.partner',  domain="[('is_dealer','=', True)]", string="Dealer")
    

