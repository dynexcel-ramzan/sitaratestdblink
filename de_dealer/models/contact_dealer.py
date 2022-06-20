# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

    


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    dealer_seq = fields.Char('Name', required=True, copy=False, readonly=True, index=True, default=lambda self: _('/'))

    is_dealer = fields.Boolean()
    date = fields.Date(string="Date")
    region = fields.Char(string="Region")
    business = fields.Char(string="Business Name:")
    exp_year = fields.Integer(string="No. of Years in Property Business:")
    

    dealer_type = fields.Selection([
        ('individual dealer', 'Individual Dealer'),
        ('dealer', 'Dealer')
    ], default='dealer', string="DEALER  TYPE:")

    selling_property_experience = fields.Selection([
        ('houses villas', 'Houses/Villas'),
        ('residential flats', 'Residential Flats'),
        ('plots', 'Plots'),
        ('commercial shops', 'Commercial/Shops'),
    ], default='plots', string="EXPERIENCE IN SELLING PROPERTY:")

    scope_of_work = fields.Selection([
        ('local city', 'Local City'),
        ('nationwide', 'Nationwide'),
    ], default='nationwide', string="SCOPE OF WORK:")

    joint_visit_done = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], default='yes', string="Joint Visit Done:")

    proposed_sales_executive = fields.Char(string="Proposed Sales Executive:")
    territory = fields.Char(string="Territory:")
    
    @api.model
    def create(self, vals):
        if vals.get('is_dealer'):
            vals['ref'] = self.env['ir.sequence'].next_by_code('dealer.sequence')
        return super(ResPartner, self).create(vals)