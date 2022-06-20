# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class AccountBatchPayment(models.Model):
    _inherit = 'account.batch.payment'
    
    city_id = fields.Many2one('res.city', string='City')