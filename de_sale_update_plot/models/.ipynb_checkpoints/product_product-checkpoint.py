# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = 'product.product' 
    
    
    def action_update_plots(self):
        for rec in self:
            if rec.state=='done':
                raise UserError('Not Allow to Re-update Sold Plot!')
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['product.product'].browse(selected_ids)
        return {
            'name': ('Plot Updateing'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'plot.update.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                'default_plot_id': self.id,
            },
#             'context': {'default_sale_id': selected_records.id,'default_reseller_id': self.partner_id.id},
        }
    