from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import requests
import json
import datetime
import base64
import re
from datetime import datetime

class Whatsapp(models.Model):
    _name = 'whatsapp.message'

    contacts_to = fields.Many2many('res.partner', 'contacts_message', 'contact_id', 'partner_id', string='Select Recipients')
    # whatsapp_account = fields.Char(string='Whatsapp Account', compute='whatsapp_account_check')
    name = fields.Many2one('whatsapp.settings', string='WhatsApp Account', compute='whatsapp_account_check')
    message = fields.Text(string='Message')
    attatchments_whatsap = fields.Many2many(comodel_name="ir.attachment",
                                     relation="files_rel",
                                     column1="doc_id",
                                     column2="attachment_id",
                                     string="Add Files")
    message_sent_id = fields.Char(string='Message sent IDs Of Chat API')

    wp_history = fields.One2many('sync.history.whatsapp', 'sync_list_id', string="Execuation History", copy=True)

    field_name = fields.Char('Whatsapp_dyn')
    # counter_wizard = 0

    # @api.onchange('contacts_to')
    def whatsapp_account_check(self):
        # print('checking')
        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        if credetionals:
            self.name = credetionals.id
            # self.env.cr.commit()
        else:
            self.name = False

    def send_message(self):
        try:
            cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')

            credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

            if not credetionals:
                raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
            else:
                self.name = credetionals.id

            if not self.contacts_to:
                raise UserError('You Have Not Selected Any Recipient!')

            if not self.message and not self.attatchments_whatsap:
                raise UserError('Please Enter Message First! Or Attach Any File To Send!')

            instance = credetionals.whatsapp_instance_id
            token = credetionals.whatsapp_token

            header = {
                'Content-type': 'application/json',
            }

            for contact in self.contacts_to:

                # availableFiles = {'doc': 'document.doc',
                #                   'gif': 'gifka.gif',
                #                   'jpg': 'jpgfile.jpg',
                #                   'png': 'pngfile.png',
                #                   'pdf': 'presentation.pdf',
                #                   'mp4': 'video.mp4',
                #                   'mp3': 'mp3file.mp3'}
                # if format in availableFiles.keys():
                #     data = {
                #         'chatId': chatId,
                #         'body': f'https://domain.com/Python/{availableFiles[format]}',
                #         'filename': availableFiles[format],
                #         'caption': f'Get your file {availableFiles[format]}'
                #     } to do work

                if not contact.mobile:
                    raise UserError(f'Recipient "{contact.name }" does not contain Mobile Number.')

                if not contact.country_id.phone_code:
                    raise UserError(f'Recipient "{contact.name }" Recipient does not contain Country. Select Country First!')

                signature_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.whatsapp_signature')
                if signature_check:
                    signature_str = ''
                    signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                    for signature in signature_list:
                        if signature:
                            signature_str += signature

                    if not self.message:
                        self.message = ''
                        self.message += '\n \n--' + signature_str + '--'
                    else:
                        self.message += '\n \n--' + signature_str + '--'

                if len(contact.mobile) < 11 or len(contact.mobile) >= 13:
                    raise UserError(f'Recipient "{contact.name}" Might Have Wrong Phone Number!')

                phone = str(contact.country_id.phone_code) + contact.mobile[-10:]

                url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"
                responce_status_code = 0
                if self.message:
                    data = json.dumps({"phone": phone, "body": self.message})
                    responce = requests.post(url, data, headers=header)
                    responce_status_code = responce.status_code

                url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
                json_response_file = 0
                if self.attatchments_whatsap:
                    for file in self.attatchments_whatsap:
                        decode_data = file.datas.decode('utf-8')
                        docode_file = f"data:{file.mimetype};base64," + decode_data
                        data_file = {
                            "phone": phone,
                            'filename': file.name,
                            "body": docode_file
                            }
                        response_file = requests.request("POST", url_files, json=data_file, headers={})
                        json_response_file = response_file.status_code
                        # print('Ending')

                if responce_status_code == 200 or json_response_file == 200:
                    # self.message_sent_id = json_responce['id']

                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + self.message if self.message else '',
                        'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                        'model': 'res.partner',
                        'res_id': contact.id,
                        'no_auto_thread': True,
                        'add_sign': True,
                    })

                    channel_search = self.env['mail.channel'].search([('channel_partner_ids', '=', contact.id)])
                    if not channel_search:
                        self.env['mail.channel'].create({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]],
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    else:
                        channel_search.write({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': contact.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, [contact.id]]],
                            'channel_message_ids': [[4, message.id]]
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    self.env.cr.commit()

                    partner = self.env['res.partner'].search([('id', '=', contact.id)])
                    contact.counter_wizard = partner.message_counter + 1
                    partner.write({
                        'message_counter': contact.counter_wizard,
                        'message_highliter': f'Whatsapp Messages:{contact.counter_wizard}'
                    })
                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Whatsapp Dashboard'
                    }
                    self.env['detail.logs'].create(logs)
                    self.env.cr.commit()
                    continue
                else:
                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, self.attatchments_whatsap.ids]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Whatsapp Dashboard'
                    }
                    self.env['detail.logs'].create(logs)
                self.env.cr.commit()
            else:
                context = dict(self._context)
                context['message'] = 'Sucessful!'
                return self.message_wizard(context)

        except Exception as e:
            raise ValidationError(e)

    def message_wizard(self, context):
        return {
            'name': ('Success'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.wizard',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }
