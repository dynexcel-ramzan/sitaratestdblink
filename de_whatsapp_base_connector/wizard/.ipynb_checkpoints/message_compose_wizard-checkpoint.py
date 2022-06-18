# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
import base64
import re
from ast import literal_eval

from odoo import _, api, fields, models, tools, _
from odoo.exceptions import UserError
from odoo.exceptions import UserError, ValidationError, Warning
import requests
import json
import datetime
import base64
import re
from datetime import datetime




# main mako-like expression pattern
EXPRESSION_PATTERN = re.compile('(\$\{.+?\})')


def _reopen(self, res_id, model, context=None):
    # save original model in context, because selecting the list of available
    # templates requires a model in context
    context = dict(context or {}, default_model=model)
    return {'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_id': res_id,
            'res_model': self._name,
            'target': 'new',
            'context': context,
            }


class MessageComposer(models.TransientModel):
    """ Generic message composition wizard. You may inherit from this wizard
        at model and view levels to provide specific features.

        The behavior of the wizard depends on the composition_mode field:
        - 'comment': post on a record. The wizard is pre-populated via ``get_record_data``
            contain template placeholders that will be merged with actual data
            before being sent to each recipient.
    """
    _name = 'whatsapp.compose.message'
    _description = 'Whatsapp composition wizard'
    _log_access = True
    _batch_size = 500
    
    
    def _default_whatsapp_instance(self):
        credential = self.env['whatsapp.settings'].search([], limit=1)
        return credential
    
    
    def _get_records(self):
        if not self.model:
            return None
        if self.use_active_domain:
            active_domain = literal_eval(self.active_domain or '[]')
            records = self.env[self.model].search(active_domain)
        elif self.res_ids:
            records = self.env[self.model].browse(literal_eval(self.res_ids))
        elif self.res_id:
            records = self.env[self.model].browse(self.res_id)
        else:
            records = self.env[self.model]

        records = records.with_context(mail_notify_author=True)
        return records
    
    
    
    
    def action_send_whatsapp(self):
        if self.model == 'res.partner':
            partner_ids = self._get_records()
            for partner in partner_ids:
                instance = self.instance_id.whatsapp_instance_id
                token = self.instance_id.whatsapp_token
                instance_url = self.instance_id.url
                header = {
                        'Content-type': 'application/json',
                    }
                phone = partner.mobile
                if not phone:
                    raise UserError(f'"{partner.name}" Recipient does not contain Mobile Number!')
                url = f"{instance_url}{instance}/sendMessage?token={token}"

                responce_status_code = 0

                data = json.dumps({"phone": phone, "body": self.body})
                responce = requests.post(url, data, headers=header)
                responce_status_code = responce.status_code
                partner.message_post(body=_('Dear %s,.') % (partner.name + self.body) ,
                          partner_ids=[self.env.user.partner_id.id]) 
                logs = {
                     'date_delivered': datetime.now(),
                     'account_id': self.instance_id.id,
                     'message': self.body,
                     'message_deliverd': 'Sucessful',
                      'partner_id': partner.id,
                    'model_id': self.model
                            }
                detail_log = self.env['whatsapp.message.log'].create(logs)
        
        else:
            instance = self.instance_id.whatsapp_instance_id
            token = self.instance_id.whatsapp_token
            instance_url = self.instance_id.url                              
            header = {
                    'Content-type': 'application/json',
                }
            purchaseorder = self._get_records()
            phone = purchaseorder.partner_id.mobile
            if not phone:
                raise UserError(f'"{self.partner_ids.name}" Recipient does not contain Mobile Number!')
            url = f"{instance_url}{instance}/sendMessage?token={token}"

            responce_status_code = 0


            signature_log = 'No'
            signature_check = self.env['ir.config_parameter'].sudo().get_param(
                        'de_whatsapp_connector.whatsapp_signature')

            if signature_check:
                signature_log = 'Yes'
                signature_str = ''
                signature_list = re.findall("\>(.*?)\<", self.env.user.signature)        
                for signature in signature_list:
                    if signature:
                        signature_str += signature

                        self.body += '\n\n--' + signature_str + '--'
            data = json.dumps({"phone": phone, "body": self.body})
            responce = requests.post(url, data, headers=header)
            responce_status_code = responce.status_code

            response_file_status_code = 0
            url_files = f"{instance_url}{instance}/sendFile?token={token}"
            if self.attachment_ids:
                for file in self.attachment_ids:
                    decode_data = file.datas.decode('utf-8')
                    docode_file = f"data:{file.mimetype};base64," + decode_data
                    data_file = {
                             "phone": phone,
                             'filename': file.name,
                             "body": docode_file ,
                    }
                    response_file = requests.request("POST", url_files, json=data_file, headers={})
                    response_file_status_code = response_file.status_code

            message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + self.body if self.body else '',
                        'attachment_ids': [[6, 0, self.attachment_ids.ids]],
                        'model': self.model,
                        'no_auto_thread': True,
                        'add_sign': True,
                       })

            logs = {
                  'date_delivered': datetime.now(),
                  'account_id': self.instance_id.id,
                  'message': self.body,
                  'partner_id' : purchaseorder.partner_id.id, 
                  'message_deliverd': 'Sucessful',
                  'signature': signature_log,
                  'attachment_id': [[6, 0, self.attachment_ids.ids]],
                  'model_id': self.model
                        }
            detail_log = self.env['whatsapp.message.log'].create(logs)
        
        
        
    def _get_partner(self):
        partner = self.env['res.partner'].search([], limit=1)
        return partner
                
                
    @api.model
    def default_get(self, fields):
        """ Handle composition mode. Some details about context keys:
            - comment: default mode, model and ID of a record the user comments
                - default_model or active_model
                - default_res_id or active_id
            - mass_message: model and IDs of records the user mass-whatsapp
                - active_ids: record IDs
                - default_model or active_model
        """
        result = super(MessageComposer, self).default_get(fields)
        result['res_ids'] = repr(self.env.context.get('active_ids'))
        # author
        missing_author = 'author_id' in fields and 'author_id' not in result

        if 'model' in fields and 'model' not in result:
            result['model'] = self._context.get('active_model')
        if 'res_id' in fields and 'res_id' not in result:
            result['res_id'] = self._context.get('active_id')
        if 'no_auto_thread' in fields and 'no_auto_thread' not in result and result.get('model'):
            # doesn't support threading
            if result['model'] not in self.env or not hasattr(self.env[result['model']], 'message_post'):
                result['no_auto_thread'] = True

        if 'active_domain' in self._context:  # not context.get() because we want to keep global [] domains
            result['active_domain'] = '%s' % self._context.get('active_domain')
        if result.get('composition_mode') == 'comment' and (set(fields) & set(['model', 'res_id', 'partner_ids', 'record_name', 'subject'])):
            result.update(self.get_record_data(result))

        filtered_result = dict((fname, result[fname]) for fname in result if fname in fields)
        return filtered_result

    # content
    subject = fields.Char('Subject')
    instance_id = fields.Many2one('whatsapp.settings', string='Instance', default=_default_whatsapp_instance)
    body = fields.Text('Contents', default='', sanitize_style=True)
    parent_id = fields.Many2one(
        'mail.message', 'Parent Message', index=True, ondelete='set null',
        help="Initial thread message.")
    template_id = fields.Many2one(
        'whatsapp.template', 'Use template', index=True,
        domain="[('model', '=', model)]")
    attachment_ids = fields.Many2many(
        'ir.attachment', 'whatsapp_compose_message_ir_attachments_rel',
        'wizard_id', 'attachment_id', 'Attachments')
    layout = fields.Char('Layout', copy=False)  # xml id of layout
    add_sign = fields.Boolean(default=True)
    res_ids = fields.Char('Document IDs')
    # origin
    author_id = fields.Many2one(
        'res.partner', 'Author', index=True,
        help="Author of the message. If not set,  may hold an message address that did not match any partner.")
    # composition
    composition_mode = fields.Selection(selection=[
        ('comment', 'Post on a document'),
        ('mass_whatsapp', 'Whatsapp Mass Message'),
        ('mass_post', 'Post on Multiple Documents')], string='Composition mode', default='comment')
    model = fields.Char('Related Document Model', index=True)
    res_id = fields.Integer('Related Document ID', index=True)
    record_name = fields.Char('Message Record Name', help="Name get of the related document.")
    use_active_domain = fields.Boolean('Use active domain')
    active_domain = fields.Text('Active domain', readonly=True)
    # characteristics
    message_type = fields.Selection([
        ('comment', 'Comment'),
        ('notification', 'System notification')],
        'Type', required=True, default='comment',
        help="Message type: whatsapp for whatsapp message, notification for system "
             "message, comment for other messages such as user replies")
    subtype_id = fields.Many2one(
        'mail.message.subtype', 'Subtype', ondelete='set null', index=True,
        default=lambda self: self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'))
  
    # destination
    no_auto_thread = fields.Boolean(
        'No threading for answers',
        help='Answers do not go in the original document discussion thread. This has an impact on the generated message-id.')
    is_log = fields.Boolean('Log an Internal Note',
                            help='Whether the message is an internal note (comment mode only)')
    partner_ids = fields.Many2many(
        'res.partner', 'whatsapp_compose_message_res_partner_rel',
        'wizard_id', 'partner_id' ,'Additional Contacts')
    # mass mode options
    notify = fields.Boolean('Notify followers', help='Notify followers of the document (mass post only)')
    auto_delete = fields.Boolean('Delete message',
        help='This option permanently removes any track of message after it\'s been sent, including from the Technical menu in the Settings, in order to preserve storage space of your Odoo database.')
    auto_delete_message = fields.Boolean('Delete Message Copy', help='Do not keep a copy of the message in the document communication history')

    @api.model
    def get_record_data(self, values):
        """ Returns a defaults-like dict with initial values for the composition
        wizard when sending an Whatsapp message related a previous Message (parent_id) or
        a document (model, res_id). This is based on previously computed default
        values. """
        result, subject = {}, False
        if values.get('parent_id'):
            parent = self.env['mail.message'].browse(values.get('parent_id'))
            result['record_name'] = parent.record_name,
            subject = tools.ustr(parent.subject or parent.record_name or '')
            if not values.get('model'):
                result['model'] = parent.model
            if not values.get('res_id'):
                result['res_id'] = parent.res_id
            partner_ids = values.get('partner_ids', list()) + parent.partner_ids.ids
            result['partner_ids'] = partner_ids
        elif values.get('model') and values.get('res_id'):
            doc_name_get = self.env[values.get('model')].browse(values.get('res_id')).name_get()
            result['record_name'] = doc_name_get and doc_name_get[0][1] or ''
            subject = tools.ustr(result['record_name'])

        re_prefix = _('Re:')
        if subject and not (subject.startswith('Re:') or subject.startswith(re_prefix)):
            subject = "%s %s" % (re_prefix, subject)
        result['subject'] = subject

        return result

  
    # ------------------------------------------------------------
    # TEMPLATES
    # ------------------------------------------------------------

    @api.onchange('template_id')
    def onchange_template_id_wrapper(self):
        self.ensure_one()
        values = self.onchange_template_id(self.template_id.id, self.composition_mode, self.model, self.res_id)['value']
        for fname, value in values.items():
            setattr(self, fname, value)

    def onchange_template_id(self, template_id, composition_mode, model, res_id):
        """ - mass_whatsapp: we cannot render, so return the template values
            - normal mode: return rendered values
            /!\ for x2many field, this onchange return command instead of ids
        """
        if template_id and composition_mode == 'mass_whatsapp':
            template = self.env['whatsapp.template'].browse(template_id)
            fields = ['subject', 'body_html',]
            values = dict((field, getattr(template, field)) for field in fields if getattr(template, field))
            if template.attachment_ids:
                values['attachment_ids'] = [att.id for att in template.attachment_ids]
        elif template_id:
            values = self.generate_whatsapp_message_for_composer(
                template_id, [res_id],
                ['subject', 'body_html', 'attachment_ids',]
            )[res_id]
            # transform attachments into attachment_ids; not attached to the document because this will
            # be done further in the posting process, allowing to clean database if message not send
            attachment_ids = []
            Attachment = self.env['ir.attachment']
            for attach_fname, attach_datas in values.pop('attachments', []):
                data_attach = {
                    'name': attach_fname,
                    'datas': attach_datas,
                    'res_model': 'whatsapp.compose.message',
                    'res_id': 0,
                    'type': 'binary',  # override default_type from context, possibly meant for another model!
                }
                attachment_ids.append(Attachment.create(data_attach).id)
            if values.get('attachment_ids', []) or attachment_ids:
                values['attachment_ids'] = [(6, 0, values.get('attachment_ids', []) + attachment_ids)]
        else:
            default_values = self.with_context(default_composition_mode=composition_mode, default_model=model, default_res_id=res_id).default_get(['composition_mode', 'model', 'res_id', 'parent_id', 'partner_ids', 'subject', 'body',  'attachment_ids',])
            values = dict((key, default_values[key]) for key in ['subject', 'body','partner_ids','attachment_ids', ] if key in default_values)

        if values.get('body_html'):
            values['body'] = values.pop('body_html')

        # This onchange should return command instead of ids for x2many field.
        values = self._convert_to_write(values)

        return {'value': values}

    def save_as_template(self):
        """ hit save as template button: current form value will be a new
            template attached to the current document. """
        for record in self:
            model = self.env['ir.model']._get(record.model or 'mail.message')
            model_name = model.name or ''
            template_name = "%s: %s" % (model_name, tools.ustr(record.subject))
            values = {
                'name': template_name,
                'subject': record.subject or False,
                'body_html': record.body or False,
                'model_id': model.id or False,
                'attachment_ids': [(6, 0, [att.id for att in record.attachment_ids])],
            }
            template = self.env['whatsapp.template'].create(values)
            # generate the saved template
            record.write({'template_id': template.id})
            record.onchange_template_id_wrapper()
            return _reopen(self, record.id, record.model, context=self._context)

    # ------------------------------------------------------------
    # RENDERING
    # ------------------------------------------------------------

    def render_message(self, res_ids):
        """Generate template-based values of wizard, for the document records given
        by res_ids. This method is meant to be inherited by whatsapp_template that
        will produce a more complete dictionary, using Jinja2 templates.

        Each template is generated for all res_ids, allowing to parse the template
        once, and render it multiple times. This is useful for mass message where
        template rendering represent a significant part of the process.

        Default recipients are also computed, based on  method
        _message_get_default_recipients. This allows to ensure a mass message has
        always some recipients specified.

        :param browse wizard: current whatsapp.compose.message browse record
        :param list res_ids: list of record ids

        :return dict results: for each res_id, the generated template values for
                              subject, body, 
        """
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]

        subjects = self.env['mail.render.mixin']._render_template(self.subject, self.model, res_ids)
        bodies = self.env['mail.render.mixin']._render_template(self.body, self.model, res_ids, post_process=True)
        default_recipients = {}
        if not self.partner_ids:
            records = self.env[self.model].browse(res_ids).sudo()
            default_recipients = records._message_get_default_recipients()

        results = dict.fromkeys(res_ids, False)
        for res_id in res_ids:
            results[res_id] = {
                'subject': subjects[res_id],
                'body': bodies[res_id],
            }
            results[res_id].update(default_recipients.get(res_id, dict()))

        # generate template-based values
        if self.template_id:
            template_values = self.generate_whatsapp_message_for_composer(
                self.template_id.id, res_ids,
                [ 'partner_to' , 'attachment_ids',])
        else:
            template_values = {}

        for res_id in res_ids:
            if template_values.get(res_id):
                # recipients are managed by the template
                results[res_id].pop('partner_ids', None)
                # remove attachments from template values as they should not be rendered
                template_values[res_id].pop('attachment_ids', None)
            else:
                template_values[res_id] = dict()
            # update template values by composer values
            template_values[res_id].update(results[res_id])

        return multi_mode and template_values or template_values[res_ids[0]]

    @api.model
    def generate_whatsapp_message_for_composer(self, template_id, res_ids, fields):
        """ Call whatsapp_template.generate_whatsapp(), get fields relevant for
            whatsapp.compose.message, transform into partner_ids """
        multi_mode = True
        if isinstance(res_ids, int):
            multi_mode = False
            res_ids = [res_ids]

        returned_fields = fields + ['partner_ids', 'attachments']
        values = dict.fromkeys(res_ids, False)

        template_values = self.env['whatsapp.template'].with_context(tpl_partners_only=True).browse(template_id).generate_whatsapp(res_ids, fields)
        for res_id in res_ids:
            res_id_values = dict((field, template_values[res_id][field]) for field in returned_fields if template_values[res_id].get(field))
            res_id_values['body'] = res_id_values.pop('body_html', '')
            values[res_id] = res_id_values

        return multi_mode and values or values[res_ids[0]]

    @api.autovacuum
    def _gc_lost_attachments(self):
        """ Garbage collect lost whastapp attachments. Those are attachments
            - linked to res_model 'whatsapp.compose.message', the composer wizard
            - with res_id 0, because they were created outside of an existing
                wizard (typically user input through Chatter or reports
                created on-the-fly by the templates)
            - unused since at least one day (create_date and write_date)
        """
        limit_date = fields.Datetime.subtract(fields.Datetime.now(), days=1)
        self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', 0),
            ('create_date', '<', limit_date),
            ('write_date', '<', limit_date)]
        ).unlink()
