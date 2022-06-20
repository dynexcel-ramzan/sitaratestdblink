# # -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class PlotDetailWizard(models.Model):
    _name = 'plot.detail.wizard'
    _description = 'Plot Detail Wizard'
    
    
    
    type = fields.Selection(selection=[
            ('available', 'Available Plots'),
            ('unconfirm', 'Un-Confirm Reserve Plots'),
            ('reserved', 'Reserved Plots'),
            ('booked', 'Booked Plots'),
            ('un_posted_sold', 'Sold Plots'),
            ('posted_sold', 'Plots Payments Detail'),   
        ], string='Type', required=True, default='date_wise')
    
   
    def check_report(self):
        data = {}
        data['form'] = self.read(['type'])[0]
        return self._print_report(data)

    
    def _print_report(self, data):
        data['form'].update(self.read(['type'])[0])
        return self.env.ref('de_property_report.open_plot_detail_report').report_action(self, data=data, config=False)