# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero, float_repr
from odoo.tools.misc import clean_context, format_date
from collections import defaultdict, OrderedDict
from odoo.addons.website.tools import get_video_embed_code

CATEGORY_SELECTION = [
    ('required', 'Required'),
    ('optional', 'Optional'),
    ('no', 'None')]

class OPPropertyType(models.Model):
    _name = 'op.property.type'
    _description = 'Property Type'
    _order = "id desc"
    
    name = fields.Char(string='Name', required=True)
    
class PremiumFactor(models.Model):
    _name = 'op.premium.factor'
    _description = 'Premium Factor'
    
    name = fields.Char(string='Name', required=True)
    percent = fields.Float(string='Percent', required=True)

class OPPropertyType(models.Model):
    _name = 'op.property.unit.type'
    _description = 'Property Unit Type'
    _order = "id desc"
    
    name = fields.Char(string='Name', required=True)
    property_type_id = fields.Many2one('op.property.type', string='Property Type')
        


class OPPropertyUnitFeature(models.Model):
    _name = 'op.property.unit.feature'
    _description = 'Property Unit Feature'
    _order = 'id desc'
    
    name = fields.Char(string='Name', required=True)
    evaluation_type = fields.Selection([
        ('boolean','Yes/No'),
        ('selection','List of Values'),
        ('text','Single Value'),
    ], default='boolean', string='Evaluation Type')
    
    feature_item_ids = fields.One2many('op.property.unit.feature.item', 'property_unit_feature_id', string='Feature Item', copy=True)
    
class OPPropertyFeatureUnitItem(models.Model):
    _name = 'op.property.unit.feature.item'
    _description = 'Unit Feature Item'
    _order = 'id desc'
    
    property_unit_feature_id = fields.Many2one('op.property.unit.feature', string='Items', readonly=False, ondelete='restrict', index=True, copy=False)
    name = fields.Char(string='Value', required=True)

    
class OPPropertyUnitFeatureGroup(models.Model):
    _name = 'op.property.unit.feature.group'
    _description = 'Property Feature Group'
    _order = "id desc"
    
    name = fields.Char(string='Name', required=True)
    property_unit_feature_group_line = fields.One2many('op.property.unit.feature.group.line', 'property_unit_feature_group_id', string='Feature', copy=True)
    display_type = fields.Selection([
        ('global','Global'),
        ('property','Property'),
        ('unit','Unit')
    ], default='global', string='Display Type')
    
class OPPropertyUnitFeatureGroupLine(models.Model):
    _name = 'op.property.unit.feature.group.line'
    _description = 'Property Unit Feature Group Line'
    _order = "id desc"
    
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
    

    
class OPPropertyAmenities(models.Model):
    _name = 'op.property.amenities'
    _description = 'Property Amenities'
    _order = "id desc"
    
    name = fields.Char(string='Name', required=True)
    percent = fields.Float(string='Premium Percent', required=True)
    
class OPProperty(models.Model):
    _name = 'op.property'
    _description = 'Property'
    _order = "id desc"
    
    name = fields.Char(related='partner_id.name', string='Property Name', required=True, store=True, readonly=False)
    sequence = fields.Integer(help='Used to order properties', default=10)
    parent_id = fields.Many2one('op.property', string='Parent Property', index=True)
    child_ids = fields.One2many('op.property', 'parent_id', string='Child Properties')
    partner_id = fields.Many2one('res.partner', string='Partner', required=True)
    property_image = fields.Binary(related='partner_id.image_1920', string="Property Image", readonly=False)
    
    street = fields.Char(compute='_compute_address', inverse='_inverse_street')
    street2 = fields.Char(compute='_compute_address', inverse='_inverse_street2')
    zip = fields.Char(compute='_compute_address', inverse='_inverse_zip')
    city = fields.Char(compute='_compute_address', inverse='_inverse_city')
    state_id = fields.Many2one(
        'res.country.state', compute='_compute_address', inverse='_inverse_state',
        string="Fed. State", domain="[('country_id', '=?', country_id)]"
    )
    
    country_id = fields.Many2one('res.country', compute='_compute_address', inverse='_inverse_country', string="Country")
    email = fields.Char(related='partner_id.email', store=True, readonly=False)
    phone = fields.Char(related='partner_id.phone', store=True, readonly=False)
    mobile = fields.Char(related='partner_id.mobile', store=True, readonly=False)
    website = fields.Char(related='partner_id.website', readonly=False)
    
    property_type_id = fields.Many2one('op.property.type', string='Property Type')
    property_area = fields.Integer(string='Property Area', size=10)
    no_of_blocks = fields.Integer(string='No. of Blocks', size=10,)
    
    property_amenities_ids = fields.Many2many("op.property.amenities", string="Amenities")
    property_location_ids = fields.Many2many("op.property.location", string="Locations")
        
    #optional fields
    has_room = fields.Selection(CATEGORY_SELECTION, string="Has Room", default="no", required=True,)

    def _compute_address(self):
        for property in self.filtered(lambda property: property.partner_id):
            address_data = property.partner_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = property.partner_id.browse(address_data['contact']).sudo()
                property.update(property._get_company_address_update(partner))
   
    def _get_company_address_field_names(self):
        """ Return a list of fields coming from the address partner to match
        on company address fields. Fields are labeled same on both models. """
        return ['street', 'street2', 'city', 'zip', 'state_id', 'country_id']

    def _get_company_address_update(self, partner):
        return dict((fname, partner[fname])
                    for fname in self._get_company_address_field_names())
    
    @api.model
    def create(self, vals):
        if not vals.get('name') or vals.get('partner_id'):
            self.clear_caches()
            return super(OPProperty, self).create(vals)
        partner = self.env['res.partner'].create({
            'name': vals['name'],
            'is_company': True,
            'image_1920': vals.get('logo'),
            'email': vals.get('email'),
            'phone': vals.get('phone'),
            'website': vals.get('website'),
            'country_id': vals.get('country_id'),
        })
        # compute stored fields, for example address dependent fields
        partner.flush()
        vals['partner_id'] = partner.id
        self.clear_caches()
        property = super(OPProperty, self).create(vals)
        # The write is made on the user to set it automatically in the multi company group.
        #self.env.user.write({'company_ids': [Command.link(property.id)]})
        
        return property
    
    def _inverse_street(self):
        for property in self:
            property.partner_id.street = property.street

    def _inverse_street2(self):
        for property in self:
            property.partner_id.street2 = property.street2

    def _inverse_zip(self):
        for property in self:
            property.partner_id.zip = property.zip

    def _inverse_city(self):
        for property in self:
            property.partner_id.city = property.city

    def _inverse_state(self):
        for property in self:
            property.partner_id.state_id = property.state_id

    def _inverse_country(self):
        for property in self:
            property.partner_id.country_id = property.country_id

    @api.onchange('state_id')
    def _onchange_state(self):
        if self.state_id.country_id:
            self.country_id = self.state_id.country_id
    
    


class OPPropertylocation(models.Model):
    _name = "op.property.location"
    _description = "Property Location"
    _order = 'complete_name'
    _rec_name = 'complete_name'

    name = fields.Char('Name', required=True)
    complete_name = fields.Char("Full Name", compute='_compute_complete_name', recursive=True, store=True)
    active = fields.Boolean('Active', default=True, help="By unchecking the active field, you may hide a location without deleting it.")
    usage = fields.Selection([
        ('view', 'Location'),
        ('block', 'Block'),
        ], string='Location Type',
        default='normal', index=True, required=True,)
    
    location_id = fields.Many2one('op.property.location', 'Parent Location', index=True, ondelete='cascade', help="The parent location that includes this location. Example : The 'Dispatch Zone' is the 'Gate 1' parent location.")
    child_ids = fields.One2many('op.property.location', 'location_id', 'Contains')
    comment = fields.Html('Additional Information')
    sequence = fields.Integer(string='Sequence', default=1)
    phase_location = fields.Boolean(string='Phase Location')
    
    @api.depends('name', 'location_id.complete_name')
    def _compute_complete_name(self):
        for location in self:
            if location.location_id:
                location.complete_name = '%s/%s' % (location.location_id.complete_name, location.name)
            else:
                location.complete_name = location.name
                
    @api.depends('child_ids.usage', 'child_ids.child_internal_location_ids')
    def _compute_child_internal_location_ids(self):
        # batch reading optimization is not possible because the field has recursive=True
        for div in self:
            div.child_internal_locaiton_ids = self.search([('id', 'child_of', div.id)])