# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    invoice_control = fields.Selection([('invoiced', 'Invoiced'),
                                        ('2binvoice', 'To Be Invoiced'),
                                        ('none', 'Not Applicable'),], 
                                       string="Invoice Control", default='2binvoice', store=True, compute='_compute_invoice_control')
    
    move_id = fields.Many2one('account.move', string='Invoice')
    move_state = fields.Selection(related='move_id.state')
    origin_picking_id = fields.Many2one('stock.picking', string='Origin Picking')
    is_return = fields.Boolean(string='Is Return', default=False)
    
    def get_invocie_count(self):
        count = self.env['account.move'].search_count([('id', '=', self.move_id.id)])
        self.invocie_count = count
        
    invocie_count = fields.Integer(string='Invocie Count', compute='get_invocie_count')
    
    
    @api.depends('state','move_id','move_state')
    def _compute_invoice_control(self):
        invoice_control = '2binvoice'
        for picking in self:
            if picking.state == 'done':
                if not picking.move_state:
                    invoice_control == '2binvoice'
                else:
                    if picking.move_state == 'cancel':
                        invoice_control = '2binvoice'
                    else:
                        invoice_control = 'invoiced'
            elif picking.state == 'cancel':
                invoice_control = 'none'
            picking.invoice_control = invoice_control
                
        
    
    def create_bill(self):
        invoice = self.env['account.move']
        move_type = ''
        if self.invoice_control == '2binvoice':
            if self.picking_type_code == 'incoming':
                move_type = self._context.get('default_move_type', 'in_invoice')
            elif self.picking_type_code == 'outgoing':
                if self.origin_picking_id.picking_type_code == 'incoming':
                #if not self.purchase_id:
                    move_type = 'in_refund'

            if not self.purchase_id:
                raise UserError(_('You cannot create vendor bill without purchase order reference.'))

            journal_id = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
            if not journal_id:
                raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

            lines_data = []
            taxes = []
            for line in self.move_lines:
                if line.purchase_line_id:
                    taxes = [(6, 0, line.purchase_line_id.taxes_id.ids)]
                else:
                    taxes = [(6, 0, line.product_id.supplier_taxes_id.ids)]
                    
                lines_data.append([0,0,{
                    'name': str(self.name) + ' ' + str(line.product_id.name),
                    #'stock_move_id': line.id,
                    'price_unit': line.purchase_line_id.price_unit or 0.0,
                    'purchase_line_id':line.purchase_line_id.id,
                    #'discount': line.discount,
                    'quantity': line.quantity_done,
                    'product_uom_id': line.product_uom.id,
                    'product_id': line.product_id.id,
                    'tax_ids':taxes,
                    #'tax_ids': [(6, 0, tax_ids.ids)],
                    #'tax_ids': [(6, 0, line.purchase_line_id.taxes_id.ids)] or [(6, 0, line.product_id.supplier_taxes_id.ids)],
                    'analytic_account_id': line.purchase_line_id.account_analytic_id.id,
                    'analytic_tag_ids': [(6, 0, line.purchase_line_id.analytic_tag_ids.ids)],
                    
                    'picking_id': self.id,
                }])
            move = invoice.create({
                'move_type': move_type,
                'picking_id': self.id,
                'purchase_id': self.purchase_id,
                'invoice_date': fields.Datetime.now(),
                'partner_id': self.partner_id.id,
                #'partner_shipping_id': self.partner_id.id,
                'currency_id': self.purchase_id.currency_id.id,
                'journal_id': journal_id.id,
                'invoice_origin': self.name,
                #'fiscal_position_id': fpos.id,
                'invoice_payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
                'narration': self.name,
                'invoice_user_id': self.user_id.id,
                #'partner_bank_id': company.partner_id.bank_ids.filtered(lambda b: not b.company_id or b.company_id == company)[:1].id,
                'invoice_line_ids':lines_data,
            })
            
            self.update({
                'move_id': move.id,
                'invoice_control': 'invoiced',
            })
        return invoice
    
    def _prepare_invoice(self):
        """Prepare the dict of values to create the new invoice for a purchase order.
        """
        self.ensure_one()
        move_type = self._context.get('default_move_type', 'in_invoice')
        journal = self.env['account.move'].with_context(default_move_type=move_type)._get_default_journal()
        if not journal:
            raise UserError(_('Please define an accounting purchase journal for the company %s (%s).') % (self.company_id.name, self.company_id.id))

        partner_invoice_id = self.partner_id.address_get(['invoice'])['invoice']
        invoice_vals = {
            'ref': 'self.partner_ref',
            'move_type': move_type,
            'narration': 'self.notes',
            'currency_id': self.purchase_id.currency_id.id,
            'invoice_user_id': self.user_id and self.user_id.id,
            'partner_id': partner_invoice_id,
            'payment_reference': '',
            'partner_bank_id': self.partner_id.bank_ids[:1].id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.partner_id.property_supplier_payment_term_id.id,
            'invoice_line_ids': [],
            'company_id': self.company_id.id,
        }
        return invoice_vals
    
    def action_view_invoice(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Bill',
            'domain': [('id','=', self.move_id.id)],
            'target': 'current',
            'res_model': 'account.move',
            'view_mode': 'tree,form',
        }

    
    
    def action_create_invoice(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['stock.picking'].browse(selected_ids)
        return {
            'name': ('Create Invoice'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'create.invoice.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_picking_ids': selected_records.ids},
        }
    
class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_account_move_line1(self, move=False):
        self.ensure_one()
        aml_currency = move and move.purchase_id.currency_id or self.picking_id.purchase_id.currency_id
        date = move and move.date or fields.Date.today()
        res = {
            #'display_type': self.display_type,
            'sequence': self.sequence,
            'name': '%s: %s' % (self.picking_id.name, self.name),
            'product_id': self.product_id.id,
            'product_uom_id': self.product_uom.id,
            'quantity': self.quantity_done,
            'price_unit': self.picking_id.purchase_id.currency_id._convert(self.purchase_line_id.price_unit, aml_currency, self.company_id, date),
            'purchase_line_id': self.purchase_line_id.id,
        }
        if not move:
            return res

        if self.currency_id == move.company_id.currency_id:
            currency = False
        else:
            currency = move.currency_id

        res.update({
            'move_id': move.id,
            'currency_id': currency and currency.id or False,
            'date_maturity': move.invoice_date_due,
            'partner_id': move.partner_id.id,
        })
        return res
    
    
    

    
    
    
    
    
