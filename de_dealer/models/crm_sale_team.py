# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class CrmTeam(models.Model):
    _inherit = 'crm.team'
    
    dealer_id = fields.Many2many('res.partner',  domain="[('is_dealer','=', True)]", string="Dealer")


    

