
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta


class PlotResellWizard(models.TransientModel):
    _name = "plot.resell.wizard"
    _description = "Plot Resell wizard"
    

    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    reseller_id = fields.Many2one('res.partner', string='Reseller')
    resell_date = fields.Date(string='Reselling Date',  required=True, default=fields.date.today())
    sale_id = fields.Many2one('sale.order', string='Order')

    def action_confirm(self):
        resell_vals={
            'partner_id': self.reseller_id.id,
            'customer_id': self.partner_id.id,
            'date': self.resell_date,
            'order_id': self.sale_id.id,
            'amount_paid': self.sale_id.amount_paid,
            'amount_residual': self.sale_id.amount_residual,
        }
        reseller = self.env['plot.reseller.line'].create(resell_vals)
        self.sale_id.update({
            'partner_id': self.partner_id.id,
        })
        payments=self.env['account.payment'].search([('order_id','=',self.sale_id.id)])
        for pay in payments:
            pay.action_draft()
            pay.update({
                'partner_id': self.partner_id.id,
            })
            pay.action_post()
        
        