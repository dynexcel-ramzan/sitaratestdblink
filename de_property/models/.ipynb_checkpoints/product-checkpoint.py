# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class ProductTemplate(models.Model):
    _inherit = "product.product"
    
    def action_unreserve_token(self):
        for line in self:
            if line.state in ('unconfirm', 'reserved'):
                line.update({
                    'state': 'available',
                    'partner_id': False,
                    'cnic': '',
                    'booking_validity': False,
                    'date_validity': False,
                    'date_reservation': False,
                    
                })
                if line.payment_ids:
                    for pay in line.payment_ids:
                        pay.action_cancel()
                    line.payment_ids.unlink()    
            else:
                raise UserError('You are not Allow to Unreserve This Product!')
    

    def action_generate_booking(self):
        for rec in self:
            if rec.booking_id:
                raise UserError(_('Selected Plot are already Booked!'))
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['product.product'].browse(selected_ids)
        return {
            'name': ('Generate Booking'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'generate.booking.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_product_ids': selected_records.ids,
                        'default_partner_id': self.partner_id.id,
                        'default_date_reservation': self.booking_validity,
                        'default_date_validity': self.date_validity,
                       },
        }
    
    def action_assign_token(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['product.product'].browse(selected_ids)
        return {
            'name': ('Assign Token Payment'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'assign.token.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_product_ids': selected_records.ids,'default_partner_id': self.partner_id.id},
        }
    
    def action_assign_partner(self):
        for rec in self:
            selected_ids = rec.env.context.get('active_ids', [])
            selected_records = rec.env['product.product'].browse(selected_ids)
        return {
            'name': ('Assign Dealer/Customer'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'assign.dealer.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'default_product_ids': selected_records.ids},
        }
    


class ProductTemplate(models.Model):
    _inherit = "product.template"

    
    def action_view_batch_payments(self):
        self.ensure_one()
        return {
         'type': 'ir.actions.act_window',
         'binding_type': 'object',
         'domain': [('order_id', '=', self.id)],
         'multi': False,
         'name': 'Payments',
         'target': 'current',
         'res_model': 'account.batch.payment',
         'view_mode': 'tree,form',
        }
    
    def get_batch_bill_count(self):
        count = self.env['account.batch.payment'].search_count([('order_id', '=', self.id)])
        self.batch_bill_count = count
        
    batch_bill_count = fields.Integer(string='Payments', compute='get_batch_bill_count')
    premium_id = fields.Many2one('op.premium.factor', string='Premium')
    standard_price = fields.Float(string="Standard price")
    list_price = fields.Float(compute='_compute_sum')
    booking_amount = fields.Float(string='Booking Amount')
    allottment_amount = fields.Float(string='Allottment Amount')
    installment_amount = fields.Float(string='Installment Amount')
    partner_id = fields.Many2one('res.partner', string='Dealer/Customer')
    cnic = fields.Char(string='CNIC')
    booking_id = fields.Many2one('sale.order', string='Booking')
    partner_role = fields.Char( string='Role')
    state = fields.Selection(selection=[
            ('available', 'Available'),
            ('unconfirm', 'Un-Confirm'),
            ('reserved', 'Reserved'),
            ('booked', 'Booked'),
            ('un_posted_sold', 'Un-Posted Sold'),
            ('posted_sold', 'Posted Sold'),
        ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='available')    
    amount_paid = fields.Float(string='Amount Paid', compute='compute_amount_total')
    amount_residual = fields.Float(string='Amount Due')
    commission_amount = fields.Float(string='Commission Amount')
    discount_amount = fields.Float(string='Discount Amount')
    date_reservation = fields.Date(string='Date of Reservation')
    booking_validity = fields.Date(string='Booking Validity')
    date_validity = fields.Date(string='Date Validity')
    
    
    
#     def action_sale_quotations_new(self):
#         for property in self:
#             vals={
#                 'partner_id': self.partner_id.id,                
#             }
#             order=self.env['sale.order'].create(vals)
    
    
    @api.depends('amount_paid', 'amount_residual', 'list_price','commission_amount','discount_amount')
    def compute_amount_total(self):
        for line in self:
            amount_paid = 0
            amount_residual = 0
            for  pay in line.payment_ids:
                if pay.state in ('draft','posted'):
                    amount_paid += pay.amount 
            amount_residual =   line.list_price - amount_paid - line.discount_amount 
            if amount_residual < 0:
                amount_residual=0
            line.amount_paid = amount_paid
            line.amount_residual = amount_residual

    

    
    @api.constrains('partner_id')
    def _check_partner(self):
        for line in self:
            if line.partner_id:
                if line.partner_id.active_dealer==True:
                    line.partner_role='Dealer'
                else:
                    line.partner_role='Customer'
            else:
                line.partner_role=' '
                    

    @api.depends('plot_area_marla','plot_file', 'property_amenities_id')
    def _compute_sum(self):
        for line in self:
            if float(line.plot_area_marla) > 0.0 and float(line.plot_file) > 0.0:
                total_amount = float(line.plot_area_marla) * float(line.plot_file)
                line.list_price = round(total_amount + (line.property_amenities_id.percent * (total_amount / 100)))
            else:
                line.list_price=0
            line.booking_amount= round(((line.list_price-line.discount_amount)/100)*10) 
            line.allottment_amount= round(((line.list_price-line.discount_amount)/100)*15)
            line.installment_amount=round(((line.list_price-line.discount_amount)/100)*75)
            
    can_be_property = fields.Boolean(string="Can be Property", compute='_compute_can_be_property',
        store=True, readonly=False, help="Specify whether the product can be selected in a property.")
    
    property_id = fields.Many2one('op.property', string='Property')
    
    payment_ids = fields.Many2many('account.payment', string='Payments', copy=False)
    
    property_location_id = fields.Many2one('op.property.location', string='Location')
    property_type_id = fields.Many2one('op.property.type')
    property_unit_type_id = fields.Many2one('op.property.unit.type', string='Unit Type')
    plot_type = fields.Selection([
        ('plot file', 'Plot File')
    ], default='plot file')
    plot_file = fields.Float(string="Rate Per Marla")
    property_amenities_id = fields.Many2one("op.property.amenities", string="Amenities")
    property_unit_feature_group_ids = fields.Many2many("op.property.unit.feature.group", string="Feature Groups", )
    amenities_percent = fields.Float(string='Premium', compute='_compute_property_amenities')
    
    @api.depends('property_amenities_id')
    def _compute_property_amenities(self):
        for line in self:
            if line.property_amenities_id:
                line.amenities_percent = line.property_amenities_id.percent
            else:
                line.amenities_percent = 0

    plot_size = fields.Char(string='Plot Size')
    road_width = fields.Char(string='Road Width')                       
    plot_area_marla = fields.Float(string='Plot Area in Marla')
    plot_area_sft = fields.Char(string='Plot Area in sft')
    

    
    property_owner_ids = fields.One2many('product.template.partner.line', 'product_tmpl_id', string='Owner Lines', copy=True, auto_join=True)
    property_feature_line = fields.One2many('product.template.feature.line', 'product_tmpl_id', string='Feature Lines', copy=True, auto_join=True)



    @api.depends('type')
    def _compute_can_be_property(self):
        self.filtered(lambda p: p.type not in ['consu', 'service']).update({'can_be_property': False})

class ProductTemplateFeatureLine(models.Model):
    _name = "product.template.feature.line"
    _description = "Product Template Feature Line"
    _order = 'product_tmpl_id, id'
    
    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade', index=True, copy=False)
    property_unit_feature_group_id = fields.Many2one('op.property.unit.feature.group', string='Feature Group', readonly=False, ondelete='restrict', index=True, copy=False)
    property_unit_feature_id = fields.Many2one('op.property.unit.feature', string='Feature')
    property_feature_evaluation_type = fields.Selection(related='property_unit_feature_id.evaluation_type')
    
    property_unit_feature_item_id = fields.Many2one('op.property.unit.feature.item', string='Item', domain="[('property_unit_feature_id','=',property_unit_feature_id)]")
    property_unit_feature_item_select = fields.Boolean(string='Yes/No', ondelete=False)
    property_unit_feature_item = fields.Char(string='Value')
    
    name = fields.Char(string='Name', compute='_compute_name', store=True)
    
    @api.depends('property_unit_feature_item_id','property_unit_feature_item_select','property_unit_feature_item')
    def _compute_name(self):
        for feature in self:
            if feature.property_unit_feature_item_id.id:
                feature.name = feature.property_unit_feature_item_id.name
            elif feature.property_unit_feature_item_select:
                feature.name = feature.property_unit_feature_item_select
            elif feature.property_unit_feature_item:
                feature.name = feature.property_unit_feature_item
                
    
class ProductTemplatePartnerLine(models.Model):
    _name = "product.template.partner.line"
    _description = "Product Template Partner Line"
    _order = 'product_tmpl_id, date_owner, id'
    
    product_tmpl_id = fields.Many2one('product.template', string='Product', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Char(string='Name',compute='_compute_name', store=True)
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    date_owner = fields.Datetime(string='Ownership Date', required=True, readonly=True, index=True, copy=False, default=fields.Datetime.now, help="Ownership date property of customers.")

        
    @api.depends('product_tmpl_id','partner_id')
    def _compute_name(self):
        for partner in self:
            if partner.partner_id:
                partner.name = str(partner.partner_id.name) + ' - ' + str(partner.product_tmpl_id.name)
                