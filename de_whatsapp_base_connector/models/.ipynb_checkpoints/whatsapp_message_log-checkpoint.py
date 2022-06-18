from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import requests
import json
import datetime
import base64
import re
from datetime import datetime


class WhatsappMessageLog(models.Model):
    _name = 'whatsapp.message.log'
    _order = 'date_delivered desc'
    _rec_name = 'partner_id'

    date_delivered = fields.Datetime('Delivered On', required=True, default=fields.Datetime.now)
    partner_id = fields.Many2one('res.partner', 'Contact', readonly=True)
    message = fields.Char(string="Message")
    message_deliverd = fields.Char('Delivered', readonly=True)
    attachment_id = fields.Many2many('ir.attachment', relation="files_rel_attachted",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Attachment", readonly=True)
    model_id = fields.Char('Model', readonly=True)
    signature = fields.Char('Signature', readonly=True)
    account_id = fields.Many2one('whatsapp.settings', 'Instance', readonly=True)
