# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date


class CreateInvoiceWizard(models.Model):
    _name = 'create.invoice.wizard'
    _description='Create Invoice Wizard'
    
    def _get_default_journal(self):
        journal = self.env['account.journal'].search([('type','=','purchase')], limit=1)
        return journal
    
    
        
    @api.model
    def default_get(self,  default_fields):
        res = super(CreateInvoiceWizard, self).default_get(default_fields)
        pickings = self.env['stock.picking'].browse(self._context.get('active_ids'))
        res.update({
            'picking_ids': [(6, 0, pickings.ids)],
        })    
        return res
    
    journal_id = fields.Many2one('account.journal', string='Journal', required=True, readonly=False, check_company=True, domain="[('type', '=', 'purchase')]", default=_get_default_journal)

    invoice_date = fields.Datetime(string='Invoice Date' , default=fields.Datetime.now, required=True)
    picking_ids = fields.Many2many('stock.picking', string='Picking')
    currency_id = fields.Many2one('res.currency', string='Currency',)
    
    
    
    def action_create_bill(self):
        """Create the invoice associated to the PO.
        """
        move_type = 'entry'
        if self.journal_id.type == 'purchase':
            move_type = 'in_invoice'
        elif self.journal_id.type == 'sale':
            move_type = 'out_invoice'    
        
        vendor_list = []
        currency_id = self.env.company.currency_id
        #pickings = self.env['stock.picking'].browse(self._context.get('active_ids', []))
        for picking in self.picking_ids:
            vendor_list.append(picking.partner_id.id)  
        uniq_vendor_list = set(vendor_list)
        
        order_list = []
        origin = ''
        for purchase in self.picking_ids.move_ids_without_package.purchase_line_id:
            order_list.append(purchase.order_id)  
        uniq_order_list = set(order_list)
        for order in order_list:
            origin += order.name + ','
            currency_id = order.currency_id.id
        
        for partner in uniq_vendor_list:
            invoice_line = []
            for picking in self.picking_ids:
                if picking.partner_id.id == partner:
                    if not picking.state == 'done':
                        raise UserError(_("Please validate delivery to create bill '%s'.", picking.name))
                    if picking.invoice_control == '2binvoice':
                        for move_line in picking.move_ids_without_package:
                            invoice_line.append((0,0, {
                                'product_id': move_line.product_id.id,
                                'currency_id': currency_id, #po_line.currency_id.id, 
                                'name': '%s: %s' % (picking.name, move_line.purchase_line_id.name),
                                'quantity': move_line.product_uom_qty if  picking.state!='done' else move_line.quantity_done, 
                                'price_unit': move_line.purchase_line_id.price_unit,
                                'partner_id': partner,
                                'purchase_line_id': move_line.purchase_line_id.id,
                                'analytic_account_id': move_line.purchase_line_id.account_analytic_id.id,
                                'analytic_tag_ids': [(6, 0, move_line.purchase_line_id.analytic_tag_ids.ids)],
                                'picking_id': picking.id,
                                'project_id': move_line.project_id.id,
                            }))
            if invoice_line:           
                vals = {
                'partner_id': partner,
                'journal_id': self.journal_id.id,
                'invoice_date': self.invoice_date,
                'move_type': move_type,
                'currency_id': currency_id,
                'invoice_origin': origin,
                'invoice_line_ids': invoice_line,   
                }
                move = self.env['account.move'].create(vals)
                
                for picking in self.picking_ids:
                    if picking.partner_id.id == partner:
                        picking.update({
                            'move_id': move.id, 
                            'invoice_control': 'invoiced',
                            })           
            else:
                raise UserError('Invoice is already created.')                 

