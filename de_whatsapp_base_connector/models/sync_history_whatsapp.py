from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import requests
import json
import datetime
import base64
import re
from datetime import datetime

class SyncHistory(models.Model):
    _name = 'sync.history.whatsapp'
    _order = 'sync_date desc'

    sync_date = fields.Datetime('Execution Date/Time', required=True, default=fields.Datetime.now)
    # contact_name = fields.Char('To Contact/Customer', readonly=True)
    contact_name = fields.Many2one('res.partner','To Contact/Customer', readonly=True)
    message_sucess = fields.Char('Successful/Error', readonly=True)
    # account_used = fields.Char('From Account', readonly=True)
    account_used = fields.Many2one('whatsapp.settings','From Account', readonly=True)

    sync_list_id = fields.Many2one('whatsapp.message', string='Partner Reference', required=True, ondelete='cascade',index=True, copy=False)
