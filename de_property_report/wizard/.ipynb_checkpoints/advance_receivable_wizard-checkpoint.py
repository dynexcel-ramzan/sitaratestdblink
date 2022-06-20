# # -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AdvanceReceivableWizard(models.Model):
    _name = 'advance.receivable.wizard'
    _description = 'Advance Receivable Wizard'
    
    
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    type = fields.Selection([
        ('date_wise', 'Date Wise'),
        ('date_wise_paid', 'Date Wise Paid'),
        ('month', 'Monthly'),
        ('year', 'Yearly'),
        ], string='Type', required=True, default='date_wise')
    
   
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'type'])[0]
        return self._print_report(data)

    
    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to', 'type'])[0])
        return self.env.ref('de_property_report.open_adv_receivable_report').report_action(self, data=data, config=False)