# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    ntn = fields.Char(string='NTN', help="The National Tax Number.")
    nic = fields.Char(string='NIC', help="The National Identity Card Number.",required=True)
    father_husband_name = fields.Char(string='Father/Husband Name')
    nationality = fields.Char(string='Nationality')
    passport = fields.Char(string='Passport')
    relation_applicant = fields.Char(string='Relation With Applicant')
    
    nominee_id = fields.Many2one('res.partner', string='nominee')
    sale_id = fields.Many2one('sale.order', string='nominee')

    
    Nominee_line_ids = fields.One2many('res.partner' , 'nominee_id'  ,string='Name')
    
    