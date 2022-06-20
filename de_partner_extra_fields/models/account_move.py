# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    vat = fields.Char(related='partner_id.vat', string='Tax ID', store=True, readonly=True)
    ntn = fields.Char(related='partner_id.ntn', string='NTN', store=True, readonly=True)
    nic = fields.Char(related='partner_id.nic', string='NIC', store=True, readonly=True)