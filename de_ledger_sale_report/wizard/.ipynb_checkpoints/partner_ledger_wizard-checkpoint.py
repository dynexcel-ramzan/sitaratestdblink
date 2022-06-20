# # -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PartnerLedgerWizard(models.Model):
    _name = 'partner.ledger.wizard'
    _description = 'Partner Ledger Wizard'
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    state = fields.Selection([
        ('draft', 'Darft'),
        ('posted', 'Posted'),
        ('all', 'All'),
    ], default='all')
   
    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from','date_to','state'])[0]
        return self._print_report(data)

    
    def _print_report(self, data):
        data['form'].update(self.read(['date_from','date_to','state'])[0])
        return self.env.ref('de_ledger_sale_report.open_partner_ledger_report').report_action(self, data=data, config=False)