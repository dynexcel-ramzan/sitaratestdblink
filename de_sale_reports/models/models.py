# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class de_sale_reports(models.Model):
#     _name = 'de_sale_reports.de_sale_reports'
#     _description = 'de_sale_reports.de_sale_reports'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
