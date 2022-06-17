# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import format_date


class AccountMove(models.Model):
    _inherit = 'account.move'
    
   
    def get_shipment_count(self):
        count = self.env['stock.picking'].search_count([('move_id', '=', self.id)])
        self.shipment_count = count
        
    #shipment_count = fields.Integer(string='Invocie Count', compute='get_shipment_count')
    picking_id = fields.Many2one('stock.picking', string='Picking', ondelete='set null', index=True)
    picking_ids = fields.Many2many('stock.picking', compute='_compute_picking', string='Receptions', copy=False, store=True)
    picking_count = fields.Integer(compute='_compute_picking', string='Picking count', default=0, store=True)
    
    

    
    @api.depends('invoice_line_ids.picking_id')
    def _compute_picking(self):
        for move in self:
            pickings = move.invoice_line_ids.mapped('picking_id')
            move.picking_ids = pickings
            move.picking_count = len(pickings)
            
    def action_view_picking(self):
        """ This function returns an action that display existing picking orders of given purchase order ids. When only one found, show the picking immediately.
        """
        result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        # override the context to get rid of the default filtering on operation type
        #result['context'] = {'default_partner_id': self.partner_id.id, 'default_origin': self.name, 'default_picking_type_id': self.picking_type_id.id}
        pick_ids = self.mapped('picking_ids')
        # choose the view_mode accordingly
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = pick_ids.id
        return result
    
    #@api.onchange('picking_id')
    def _onchange_picking_id(self):
        if not self.picking_id:
            return
        # Copy data from Custom Entry
        invoice_vals = self.picking_id.with_company(self.custom_entry_id.company_id)._prepare_invoice()
        #del invoice_vals['ref']
        self.update(invoice_vals)

        # Copy Bill lines.
        #move_lines = self.picking_id.move_lines - self.line_ids.mapped('stock_move_id')
        new_lines = self.env['account.move.line']
        for line in move_lines:
            new_line = new_lines.new(line._prepare_account_move_line(self))
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()
    
    def action_view_shipment(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'binding_type': 'action',
            'name': 'Invocies',
            'domain': [('move_id','=', self.id)],
            'target': 'current',
            'res_model': 'stock.picking',
            'view_mode': 'tree,form',
        }

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    #stock_move_id = fields.Many2one('stock.move', 'Stock Move Lines', ondelete='set null', index=True, copy=False)
    picking_id = fields.Many2one('stock.picking', readonly=True) 
    
 

    
    
    
    
    
