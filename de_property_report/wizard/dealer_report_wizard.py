# # -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class DealerReportWizard(models.Model):
    _name = 'dealer.report.wizard'
    _description = 'Dealer Report Wizard'
    
    
    date_from = fields.Date(string='Date From', required=True,default=fields.date.today())
    date_to = fields.Date(string='Date To', required=True,default=fields.date.today())
    type = fields.Selection([
        ('summary', 'Summary'),
        ('detail', 'Detail'),
        ], string='Type', required=True, default='summary')
    
   
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'type'])[0]
        return self._print_report(data)

    
    def _print_report(self, data):
        data['form'].update(self.read(['date_from', 'date_to', 'type'])[0])
        return self.env.ref('de_property_report.open_dealer_book_report').report_action(self, data=data, config=False)