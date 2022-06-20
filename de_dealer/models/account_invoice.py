# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.depends('dealer_id','invoice_origin')
    def _get_dealer(self):
        for line in self:
            rec = self.env['sale.order'].search([('name', '=', line.invoice_origin)])
            line.dealer_id = rec.dealer_id
     
    dealer_id = fields.Many2one('res.partner',compute="_get_dealer", store=True,Readonly=True, string="Dealer",)
    
        