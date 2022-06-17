# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    is_downpayment = fields.Boolean(string='Downpayment', compute='_compute_downpayment', default=False, store=True)
    
    @api.depends('invoice_line_ids','invoice_line_ids.purchase_line_id')
    def _compute_downpayment(self):
        #downpayment_lines = self.mapped('line_ids.purchase_line_id').filtered(lambda line: line.is_downpayment)
        #move_lines = self.env['account.move.line'].search([('journal_id.type','=','purchase'),('purchase_line_id.is_downpayment','=',True)])
        #is_downpayment = downpayment_lines
        move_lines = self.env['account.move.line']
        for move in self: #.filtered(lambda m: m.journal_id.type == 'purchase'):
            is_downpayment = False
            #move_lines = self.mapped('line_ids').filtered(lambda line: line.purchase_line_id.is_downpayment and line.move_id = move.id)
            #move_lines = self.env['account.move.line'].search([('journal_id.type','=','purchase'),('purchase_line_id.is_downpayment','=',True),('move_id','=',move.id)])
            for line in move.invoice_line_ids:
                if line.purchase_line_id.is_downpayment:
                    is_downpayment = True
            move.write({
                'is_downpayment': is_downpayment,
            })