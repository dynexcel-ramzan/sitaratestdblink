# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    active_dealer = fields.Boolean(string='Is Dealer')
    
    
    @api.model
    def create(self, vals):
        if 'nic' in vals:
            if vals['nic']:
                nic = vals['nic'].strip().lower()
                 
                sql = """ select lower(nic) from res_partner where lower(nic)='""" +str(nic)+"""' """
                self.env.cr.execute(sql)
                exists = self.env.cr.fetchone()
                
                if exists:
                    raise UserError(('Same CNIC number already exists with another contact!'))
                else:
                    pass

        rec = super(ResPartner, self).create(vals)
        return rec