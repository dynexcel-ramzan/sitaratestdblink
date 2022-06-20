# # -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class AccLedgerWizard(models.Model):
    _name = 'acc.ledger.wizard'
    _description = 'Account Ledger Wizard'
    
    
    date_from = fields.Date(string='Date From', required=True,  default=fields.date.today().replace(day=1) )
    date_to = fields.Date(string='Date To', required=True,  default=fields.date.today() )
    
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from','date_to'])[0]
        return self._print_report(data)

    
    def _print_report(self, data):
        data['form'].update(self.read(['date_from','date_to'])[0])
        return self.env.ref('de_sale_reports.open_acc_ledger_report').report_action(self, data=data, config=False)
    
    

