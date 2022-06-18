from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import requests
import json
import datetime
import base64
import re
from datetime import datetime


class Logs(models.Model):
    _name = 'detail.logs'
    _order = 'sync_date desc'
    _rec_name = 'contact_name'

    sync_date = fields.Datetime('Execution Date/Time', required=True, default=fields.Datetime.now)
    contact_name = fields.Many2one('res.partner', 'To Contact/Customer', readonly=True)
    employee_name = fields.Many2one('hr.employee', 'To Employee', readonly=True)
    message_sucess = fields.Char('Successful/Error', readonly=True)
    # files_attachted = fields.Char('Files Attached', readonly=True)
    files_attachted = fields.Many2many('ir.attachment', relation="files_rel_attachted",
                                            column1="doc_id",
                                            column2="attachment_id",
                                            string="Files Attached", readonly=True)
    from_model = fields.Char('From Model', readonly=True)
    signature_att = fields.Char('Along Signature', readonly=True)
    account_used = fields.Many2one('whatsapp.settings', 'From Account', readonly=True)
