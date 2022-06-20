from odoo import models, fields, api, _
from odoo.exceptions import UserError

class saleorder(models.Model):
    _inherit = 'sale.order'
    
    @api.constrains('partner_id')
    def _check_partner(self):
        if self.partner_id:
             self.father_husband_name = self.partner_id.father_husband_name
             self.nic = self.partner_id.nic
             self.nationality = self.partner_id.nationality
             self.passport = self.partner_id.passport
             self.ntn = self.partner_id.ntn
             self.street = self.partner_id.street
             self.phone = self.partner_id.phone
             self.mobile = self.partner_id.mobile
             self.Nominee_line_ids=self.partner_id.Nominee_line_ids
    @api.depends('partner_id.nic','partner_id.father_husband_name','partner_id.nationality','partner_id.passport','partner_id.ntn','partner_id.street','partner_id.phone','partner_id.mobile','partner_id.Nominee_line_ids')
    def _compute_partner_detail(self):
        self.father_husband_name = self.partner_id.father_husband_name
        self.nic = self.partner_id.nic
        self.nationality = self.partner_id.nationality
        self.passport = self.partner_id.passport
        self.ntn = self.partner_id.ntn
        self.street = self.partner_id.street
        self.phone = self.partner_id.phone
        self.mobile = self.partner_id.mobile
        self.Nominee_line_ids=self.partner_id.Nominee_line_ids
        self.mobile_num = self.partner_id.phone
     


    
                
   
             
                
    
    father_husband_name= fields.Char(string='Father/Husband Name')
    nic= fields.Char(string='CNIC/NICOP')
    nationality= fields.Char(string='Nationality')
    passport= fields.Char(string='Passport')
    ntn= fields.Char(string='NTN')
    street= fields.Char(string='Address')
    phone= fields.Char(string='Phone#')
    mobile= fields.Char(string='Mobile')
    relation_applicant = fields.Char(string='Relation With Applicant')
        
    Nominee_line_ids = fields.Many2many('res.partner'   , string='Name')
    
    mobile_num= fields.Char(string='num',compute='_compute_partner_detail')
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    plot_type = fields.Char(string="Plot Type")
    rate_area_marla = fields.Char(string='Rate Area Marla')
    size = fields.Char(string="Size")
    
    
    @api.constrains('product_id')
    def _check_partner(self):
        if self.product_id:
            self.plot_type = self.product_id.property_type_id.name
            self.rate_area_marla = round(self.product_id.plot_file,2)
            self.size = round(self.product_id.plot_area_marla,2)
    

