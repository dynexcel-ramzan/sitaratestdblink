from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import requests
import json
import datetime
import base64
import re
from datetime import datetime


class ResPartner(models.Model):
    _inherit = 'res.partner'

    message_counter = fields.Integer('Message Counter')
    message_highliter = fields.Char('Message Highlight')
    history_count = fields.Integer('History Counter', compute='history_counter')
    last_msg_sent = fields.Char('Last Message Number')
    counter_wizard = fields.Char('Counter')
    # dicuss_history = fields.Char('Fetch History', compute='discuss_call')

    def send_msg(self):
        # print('xyz')

        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        # self.discuss_call()

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_contacts_to': [[6, 0, [self.id]]],
                            'default_whatsapp_account': credetionals.id,
                            'default_record_id': self.id,
                            'default_model_name': str(self._inherit)},
                }

    def multi_send_msg(self):
        # print("xyz")

        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        # self.discuss_call()

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                # 'res_id': new_id.id,
                'context': {
                        'default_contacts_to': [[6, 0, self.ids]],
                        'default_whatsapp_account': credetionals.id,
                        # 'default_record_id': self.id,
                        'default_model_name': str(self._inherit),
                        'default_selection_check': 0,
                        'default_invisible_check': 1,
                },
                }

    def wa_history(self):
        return {
            'name': (_('WhatsApp History')),
            'domain': [('from_model', '=', 'Contacts'), ('contact_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'detail.logs',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def history_counter(self):
        self.history_count = len(self.env['detail.logs'].search([('from_model', '=', 'Contacts'), ('contact_name', '=', self.id)]))

    def discuss_call(self):
        try:
            # self.last_msg_sent = 0
            cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
            credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

            instance = credetionals.whatsapp_instance_id
            token = credetionals.whatsapp_token

            url = f"https://eu38.chat-api.com/instance{instance}/messages?token={token}&last={20}&chatId={str(self.country_id.phone_code) + self.mobile[-10:]}@c.us&limit={20}"

            header = {
                'Content-type': 'application/json',
            }

            responce = requests.get(url, headers=header)
            responce_status_code = responce.status_code
            responce_json = responce.json()['messages']

            msg_ids = []
            for msg in responce_json:
                message = None
                if msg['fromMe'] == False and msg['messageNumber'] > int(self.last_msg_sent) and msg['type'] == 'chat':
                # if msg['fromMe'] == False and msg['type'] == 'chat':
                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': f'From {self.name}: ' + msg['body'],
                        # 'attachment_ids': [[6, 0, self.attatchments_whatsap.ids]],
                        # 'model': self.model_name,
                        # 'res_id': contact.id,
                        'no_auto_thread': True,
                        'add_sign': True,
                    })
                    self.last_msg_sent = str(msg['messageNumber'])
                    # msg_ids.append(message.id)

                    channel_search = self.env['mail.channel'].search([('channel_partner_ids','=', self.id)])
                    if not channel_search and message:
                        self.env['mail.channel'].create({
                            # 'sl_slack_channel_id': channel_search.id,
                            'name': self.name,
                            'alias_user_id': self.env.user.id,
                            'is_subscribed': True,
                            'is_member': True,
                            'channel_partner_ids': [[6, 0, self.ids]],
                            'channel_message_ids': [[4, message.id]],
                        })
                    else:
                        if message:
                            channel_search.write({
                                # 'sl_slack_channel_id': channel_search.id,
                                'name': self.name,
                                'alias_user_id': self.env.user.id,
                                'is_subscribed': True,
                                'is_member': True,
                                'channel_partner_ids': [[6, 0, [self.id]]],
                                'channel_message_ids': [[4, message.id]],
                            })
            self.env.cr.commit()

        except Exception as e:
            pass

    def wa_discuss(self):
        # self.discuss_call()

        channel = self.env['mail.channel'].search([('name', '=', self.name)])
        if not channel.is_member and not channel.is_subscribed:
            channel.write({
                'is_member': True,
                'is_subscribed': True,
            })

        self.ensure_one()
        channel_partner = channel.mapped('channel_last_seen_partner_ids').filtered(
            lambda cp: cp.partner_id == self.env.user.partner_id)
        # if not channel_partner:
        #     return channel.write({'channel_last_seen_partner_ids': [(0, 0, {'partner_id': self.env.user.partner_id.id})]})

        return {'type': 'ir.actions.client',
                'res_model': 'mail.channel',
                'tag': 'mail.widgets.discuss',
                'context': {'active_id': f'mail.channel_{channel.id}'}
                # 'context': {'active_id': channel.id}
                }


class ResSaleOrder(models.Model):
    _inherit = 'sale.order'

    message_counter_sales = fields.Integer('Message Counter')
    message_sales = fields.Char('Message')
    history_count = fields.Integer('History Counter', compute='history_counter')

    def send_msg(self):
        report = self.env.ref('sale.action_report_saleorder').report_action(self)
        report_id = self.env.ref('sale.action_report_saleorder')
        pdf, data = report_id.sudo()._render(self.id)
        pdf64 = base64.b64encode(pdf)
        attachment_id = self.env['ir.attachment'].create(
            {
                "name": f"{self.type_name} - {self.name}",
                "datas": pdf64
            }
        )

        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        quotation_sale_check = self.env['ir.config_parameter'].sudo().get_param(
            'de_whatsapp_connector.quotation_orders')

        if quotation_sale_check:
            self.message_sales = f"""Hello {self.partner_id.name},\nPlease Acknowledge Attached {self.type_name} Report.\n
The {self.type_name} "{self.name}" Contain Following {len(self.order_line)} Products With Total Amount {self.amount_total}.\n"""
            new_message = ''
            for order in self.order_line:
                new_message += f"""----------------------------\nPrduct Name: {order.name}\nQty: {order.product_uom_qty}\nUnit Price: {order.price_unit}\nSubtotal: {order.price_subtotal}\n"""

            self.message_sales += new_message + '----------------------------'
        else:
            self.message_sales = ''

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_contacts_to': [[6, 0, [self.partner_id.id]]],
                    'default_attatchments_whatsap': [[6, 0, [attachment_id.id]]],
                    'default_whatsapp_account': credetionals.id,
                    'default_record_id': self.id,
                    'default_message': self.message_sales,
                    'default_model_name': str(self._inherit),
                    'selection_check': 1,
                },
                }

    def multi_send_msg(self):
        # print("xyz")

        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                # 'res_id': new_id.id,
                'context': {
                    'default_contacts_to': [[6, 0, self.partner_id.ids]],
                            'default_whatsapp_account': credetionals.id,
                            'default_many_sales_record_ids': [[6, 0, self.ids]],
                            # 'default_record_id': self.id,
                            'default_model_name': str(self._inherit)
                },
                }

    def whatsap_Saleorder(self):
        try:
            cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
            credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

            if not credetionals:
                raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
            # else:
            #     self.name = credetionals.id

            if not self:
                raise UserError('You Have Not Selected Any Quatation/Sale Order!')

            instance = credetionals.whatsapp_instance_id
            token = credetionals.whatsapp_token

            header = {
                'Content-type': 'application/json',
            }

            for order in self:
                messagez = ''
                contact = order.partner_id
                if not contact.country_id.phone_code:
                    raise UserError(f'"{contact.name}" Recipient does not contain Country. Select Country First!')

                signature_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.whatsapp_signature')

                quotation_sale_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.quotation_orders')

                if quotation_sale_check:
                    order.message_sales = f"""Hello {contact.name},\nPlease Acknowledge Attached {order.type_name} Report.\n
The {order.type_name} "{order.name}" Contain Following {len(order.order_line)} Products With Total Amount {order.amount_total}.\n"""

                    new_message = ''

                    for order_line in order.order_line:
                        new_message += f"""----------------------------\nPrduct Name: {order_line.name}\nQty: {order_line.product_uom_qty}\nUnit Price: {order_line.price_unit}\nSubtotal: {order_line.price_subtotal}\n"""

                    order.message_sales += new_message + '----------------------------'
                else:
                    order.message_sales = f'Hello {contact.name},\nPlease Acknowledge Attached {order.type_name} Report. \n \n'

                if signature_check:
                    signature_str = ''
                    signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                    for signature in signature_list:
                        if signature:
                            signature_str += signature

                    order.message_sales += '\n\n--' + signature_str + '--'

                phone = str(contact.country_id.phone_code) + contact.mobile[-10:]

                if len(phone) < 11 or len(phone) > 13:
                    raise UserError(f'"{contact}" Might Have Wrong Phone Number!')

                url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"

                responce_status_code = 0
                data = json.dumps({"phone": phone, "body": order.message_sales})
                responce = requests.post(url, data, headers=header)
                responce_status_code = responce.status_code

                report = self.env.ref('sale.action_report_saleorder').report_action(order)
                report_id = self.env.ref('sale.action_report_saleorder')
                pdf, data = report_id.sudo()._render(order.id)
                pdf64 = base64.b64encode(pdf)
                attachment_id = self.env['ir.attachment'].create(
                    {
                        "name": f"{order.type_name} - {order.name}",
                        "datas": pdf64
                    }
                )

                url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
                json_response_file = 0

                decode_data = attachment_id.datas.decode('utf-8')
                docode_file = f"data:{attachment_id.mimetype};base64," + decode_data
                data_file = {
                    "phone": phone,
                    'filename': attachment_id.name,
                    "body": docode_file
                }
                response_file = requests.request("POST", url_files, json=data_file, headers={})
                json_response_file = response_file.status_code
                # print('Ending')

                if responce_status_code == 200 or json_response_file == 200:
                    # self.message_sent_id = json_responce['id']

                    order.write({
                        'message_counter_sales': order.message_counter_sales + 1,
                    })
                    p = self.env['res.partner'].search([('id', '=', contact.id)])
                    x = p.message_counter + 1
                    p.write({
                        'message_counter': x,
                        'message_highliter': f'Whatsapp Messages:{x}'
                    })

                    messagez = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + order.message_sales,
                        'attachment_ids': [[6, 0, [attachment_id.id]]],
                        'model': 'sale.order',
                        'res_id': order.id,
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
                            'channel_message_ids': [[4, messagez.id]],
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
                            'channel_message_ids': [[4, messagez.id]]
                            # 'channel_message_ids': [[6, 0, [message.id]]]
                        })
                    self.env.cr.commit()

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Sales'
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
                        'message_sucess': 'Error',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Sales'
                    }
                    self.env['detail.logs'].create(logs)
                self.env.cr.commit()
            else:
                context = dict(self._context)
                context['message'] = 'Sucessful!'
                return self.message_wizard(context)

        except Exception as e:

            logs = {
                # 'sync_list_id': self.id,
                'sync_date': datetime.now(),
                'contact_name': contact.id,
                'account_used': credetionals.id,
                'message_sucess': 'Error',
                'files_attachted': [[6, 0, [attachment_id.id]]],
                'signature_att': 'Yes' if signature_check else 'No',
                'from_model': 'Sales'
            }
            self.env['detail.logs'].create(logs)
            self.env.cr.commit()

            raise ValidationError(e)

    def wa_history(self):
        return {
            'name': (_('WhatsApp History')),
            'domain': [('from_model', '=', 'Sales'), ('contact_name', '=', self.partner_id.id)],
            'view_type': 'form',
            'res_model': 'detail.logs',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def history_counter(self):
        self.history_count = len(self.env['detail.logs'].search([('from_model', '=', 'Sales'), ('contact_name', '=', self.partner_id.id)]))

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

class ResAccountMove(models.Model):
    _inherit = 'account.move'

    message_counter_invoice = fields.Integer('Message Counter')
    message_sales = fields.Char('Message Invoice')
    history_count = fields.Integer('History Counter', compute='history_counter')

    def send_msg(self):
        # print('xyz')
        # list_of_ids = []
        report_id = self.env.ref('account.account_invoices')
        if report_id:
            pdf, data = report_id.sudo()._render(self.id)
            pdf64 = base64.b64encode(pdf)
            attachment_invoice = self.env['ir.attachment'].create(
                {
                    "name": f"{self.type_name} - {self.name}",
                    'type': 'binary',
                    "datas": pdf64
                }
            )
        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        invoices_check = self.env['ir.config_parameter'].sudo().get_param(
            'de_whatsapp_connector.invoices')

        if invoices_check:
            self.message_sales = f"""Hello {self.partner_id.name},\nPlease Acknowledge Attached {self.type_name} Report.\n
The {self.type_name} "{self.name}" Contain Following {len(self.invoice_line_ids)} Products With Total Amount {self.amount_total}.\n"""
            new_message = ''
            for order in self.invoice_line_ids:
                new_message += f"""----------------------------\nPrduct Name: {order.name}\nQty: {order.quantity}\nUnit Price: {order.price_unit}\nSubtotal: {order.price_subtotal}\n"""

            self.message_sales += new_message + '----------------------------'
        else:
            self.message_sales = ''

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {
                    'default_contacts_to': [[6, 0, [self.partner_id.id]]],
                    'default_attatchments_whatsap': [[6, 0, [attachment_invoice.id]]],
                    'default_whatsapp_account': credetionals.id,
                    'default_record_id': self.id,
                    'default_message': self.message_sales,
                    'default_model_name': str(self._inherit)
                    },
                }

    def whatsap_invoice(self):
        try:
            cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
            credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

            if not credetionals:
                raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
            # else:
            #     self.name = credetionals.id

            if not self:
                raise UserError('You Have Not Selected Any Quotation/Sale Order!')

            instance = credetionals.whatsapp_instance_id
            token = credetionals.whatsapp_token

            header = {
                'Content-type': 'application/json',
            }

            for order in self:

                message = ''
                contact = order.partner_id
                if not contact.country_id.phone_code:
                    raise UserError(f'"{contact.name}" Recipient does not contain Country. Select Country First!')

                signature_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.whatsapp_signature')

                invoices_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.invoices')

                if invoices_check:
                    order.message_sales = f"""Hello {contact.name},\nPlease Acknowledge Attached {order.type_name} Report.\n
The {order.type_name} "{order.name}" Contain Following {len(order.invoice_line_ids)} Products With Total Amount {order.amount_total}.\n"""

                    for order_line in order.invoice_line_ids:
                        message += f"""----------------------------\nProduct Name: {order_line.name}\nQty: {order_line.quantity}\nUnit Price: {order_line.price_unit}\nSubtotal: {order_line.price_subtotal}\n"""

                    order.message_sales += message + '----------------------------'
                else:
                    order.message_sales = f'Hello {contact.name},\nPlease Acknowledge Attached {order.type_name} Report.'
                    message += order.message_sales

                # message = f'Hello {contact.name},\nPlease Acknowledge Attached {order.type_name} Report.\n \n'

                if signature_check:
                    signature_str = ''
                    signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                    for signature in signature_list:
                        if signature:
                            signature_str += signature

                    order.message_sales += '\n\n--' + signature_str + '--'

                phone = str(contact.country_id.phone_code) + contact.mobile[-10:]

                if len(phone) < 11 or len(phone) > 13:
                    raise UserError(f'"{contact}" Might Have Wrong Phone Number!')

                url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"

                responce_status_code = 0
                data = json.dumps({"phone": phone, "body": order.message_sales})
                responce = requests.post(url, data, headers=header)
                responce_status_code = responce.status_code

                report = self.env.ref('account.account_invoices').report_action(order)
                report_id = self.env.ref('account.account_invoices')
                pdf, data = report_id.sudo()._render(order.id)
                pdf64 = base64.b64encode(pdf)
                attachment_id = self.env['ir.attachment'].create(
                    {
                        "name": f"{order.type_name} - {order.name}",
                        "datas": pdf64
                    }
                )

                url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
                json_response_file = 0

                decode_data = attachment_id.datas.decode('utf-8')
                docode_file = f"data:{attachment_id.mimetype};base64," + decode_data
                data_file = {
                    "phone": phone,
                    'filename': attachment_id.name,
                    "body": docode_file
                }
                response_file = requests.request("POST", url_files, json=data_file, headers={})
                json_response_file = response_file.status_code
                # print('Ending')

                if responce_status_code == 200 or json_response_file == 200:
                    # self.message_sent_id = json_responce['id']

                    order.write({
                        'message_counter_invoice': order.message_counter_invoice + 1,
                    })
                    p = self.env['res.partner'].search([('id', '=', contact.id)])
                    x = p.message_counter + 1
                    p.write({
                        'message_counter': x,
                        'message_highliter': f'Whatsapp Messages:{x}'
                    })

                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + message,
                        'attachment_ids': [[6, 0, [attachment_id.id]]],
                        'model': 'account.move',
                        'res_id': order.id,
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

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Invoicing'
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
                        'message_sucess': 'Error',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Invoicing'
                    }
                    self.env['detail.logs'].create(logs)
                self.env.cr.commit()
            else:
                context = dict(self._context)
                context['message'] = 'Sucessful!'
                return self.message_wizard(context)

        except Exception as e:
            logs = {
                # 'sync_list_id': self.id,
                'sync_date': datetime.now(),
                'contact_name': contact.id,
                'account_used': credetionals.id,
                'message_sucess': 'Error',
                'files_attachted': [[6, 0, [attachment_id.id]]],
                'signature_att': 'Yes' if signature_check else 'No',
                'from_model': 'Invoicing'
            }
            self.env['detail.logs'].create(logs)
            self.env.cr.commit()

            raise ValidationError(e)

    def wa_history(self):
        return {
            'name': (_('WhatsApp History')),
            'domain': [('from_model', '=', 'Invoicing'), ('contact_name', '=', self.partner_id.id)],
            'view_type': 'form',
            'res_model': 'detail.logs',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def history_counter(self):
        self.history_count = len(self.env['detail.logs'].search([('from_model', '=', 'Invoicing'), ('contact_name', '=', self.partner_id.id)]))

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


class ResHRModel(models.Model):
    _inherit = 'hr.employee'

    message_counter_employee = fields.Integer('Message Counter')
    message_highliter = fields.Char('Message Highlight')
    history_count = fields.Integer('History Counter', compute='history_counter')
    counter_wizard = fields.Char('Counter')

    def send_msg(self):
        # print('xyz')
        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard.employee',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_contacts_to': [[6, 0, [self.id]]],
                            'default_whatsapp_account': credetionals.id,
                            'default_record_id': self.id,
                            'default_model_name': str(self._inherit)
                            },
                }

    def wa_history(self):
        return {
            'name': (_('WhatsApp History')),
            'domain': [('from_model', '=', 'Employee'), ('employee_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'detail.logs',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def history_counter(self):
        self.history_count = len(self.env['detail.logs'].search([('from_model', '=', 'Employee'), ('employee_name', '=', self.id)]))

    def multi_send_msg(self):
        # print("xyz")

        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard.employee',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                # 'res_id': new_id.id,
                'context': {
                    'default_contacts_to': [[6, 0, self.ids]],
                            'default_whatsapp_account': credetionals.id,
                            # 'default_record_id': self.id,
                            'default_model_name': str(self._inherit),
                    'default_selection_check': 0,
                    'default_invisible_check': 1,
                },
                }


class ResPayments(models.Model):
    _inherit = 'account.payment'

    msg_count_pay = fields.Integer('Message Counter')
    msg_highlite = fields.Char('Message Highlight')
    message_sales = fields.Char('Message Payment')
    history_count = fields.Integer('History Counter', compute='history_counter')

    def send_msg(self):
        # print('xyz')

        report_id = self.env.ref('account.action_report_payment_receipt')
        if report_id:
            pdf, data = report_id.sudo()._render(self.id)
            pdf64 = base64.b64encode(pdf)
            attachment_invoice = self.env['ir.attachment'].create(
                {
                    # "name": f"{self.type_name} - {self.name}",
                    "name": self.display_name,
                    'type': 'binary',
                    "datas": pdf64
                }
            )

        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        payment_check = self.env['ir.config_parameter'].sudo().get_param(
            'de_whatsapp_connector.payment')

        if payment_check:
            self.message_sales = f"""Hello {self.partner_id.name},\nPlease Acknowledge Attached {self.state} Report.\n
The {self.state} "{self.name}" Contain Following Information\n"""
            self.message_sales += f"""----------------------------\nAmount: {self.amount}\nJournal: {self.journal_id.name}\nDate: {self.date}\n----------------------------"""

        else:
            self.message_sales = ''

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard.payments',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_contacts_to': [[6, 0, self.partner_id.ids]],
                            'default_whatsapp_account': credetionals.id,
                            'default_attatchments_whatsap': [[6, 0, [attachment_invoice.id]]],
                            'default_record_id': self.id,
                            'default_message': self.message_sales,
                            'default_model_name': str(self._inherit),
                            # 'default_contacts_to': 1,
                            },
                }

    def whatsapp_payments(self):
        try:
            cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
            credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

            if not credetionals:
                raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
            # else:
            #     self.name = credetionals.id

            if not self:
                raise UserError('You Have Not Selected Any Payments!')

            instance = credetionals.whatsapp_instance_id
            token = credetionals.whatsapp_token

            header = {
                'Content-type': 'application/json',
            }

            for order in self:

                contact = order.partner_id
                if not contact.country_id.phone_code:
                    raise UserError(f'"{contact.name}" Recipient does not contain Country. Select Country First!')

                signature_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.whatsapp_signature')

                payment_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.payment')

                if payment_check:
                    order.message_sales = f"""Hello {order.partner_id.name},\nPlease Acknowledge Attached {order.state} Report.\n
The {order.state} "{order.name}" Contain Following Information\n"""
                    order.message_sales += f"""----------------------------\nAmount: {order.amount}\nJournal: {order.journal_id.name}\nDate: {order.date}\n----------------------------"""

                else:
                    order.message_sales = f'Hello {contact.name},\nPlease Acknowledge Attached {order.display_name} Report. \n'

                if signature_check:
                    signature_str = ''
                    signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                    for signature in signature_list:
                        if signature:
                            signature_str += signature

                    order.message_sales += '\n \n--' + signature_str + '--'

                phone = str(contact.country_id.phone_code) + contact.mobile[-10:]

                if len(phone) < 11 or len(phone) > 13:
                    raise UserError(f'"{contact}" Might Have Wrong Phone Number!')

                url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"

                responce_status_code = 0
                data = json.dumps({"phone": phone, "body": order.message_sales})
                responce = requests.post(url, data, headers=header)
                responce_status_code = responce.status_code

                report = self.env.ref('account.action_report_payment_receipt').report_action(order)
                report_id = self.env.ref('account.action_report_payment_receipt')
                pdf, data = report_id.sudo()._render(order.id)
                pdf64 = base64.b64encode(pdf)
                attachment_id = self.env['ir.attachment'].create(
                    {
                        "name": f"{order.state}",
                        "datas": pdf64
                    }
                )

                url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
                json_response_file = 0

                decode_data = attachment_id.datas.decode('utf-8')
                docode_file = f"data:{attachment_id.mimetype};base64," + decode_data
                data_file = {
                    "phone": phone,
                    'filename': attachment_id.name,
                    "body": docode_file
                }
                response_file = requests.request("POST", url_files, json=data_file, headers={})
                json_response_file = response_file.status_code
                # print('Ending')

                if responce_status_code == 200 or json_response_file == 200:
                    # self.message_sent_id = json_responce['id']

                    order.write({
                        'msg_count_pay': order.msg_count_pay + 1,
                    })
                    p = self.env['res.partner'].search([('id', '=', contact.id)])
                    x = p.message_counter + 1
                    p.write({
                        'message_counter': x,
                        'message_highliter': f'Whatsapp Messages:{x}'
                    })

                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + order.message_sales,
                        'attachment_ids': [[6, 0, [attachment_id.id]]],
                        'model': 'account.payment',
                        'res_id': order.id,
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

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Account Payments'
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
                        'message_sucess': 'Error',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Account Payments'
                    }
                    self.env['detail.logs'].create(logs)
                self.env.cr.commit()
            else:
                context = dict(self._context)
                context['message'] = 'Sucessful!'
                return self.message_wizard(context)

        except Exception as e:
            logs = {
                # 'sync_list_id': self.id,
                'sync_date': datetime.now(),
                'contact_name': contact.id,
                'account_used': credetionals.id,
                'message_sucess': 'Error',
                'files_attachted': [[6, 0, [attachment_id.id]]],
                'signature_att': 'Yes' if signature_check else 'No',
                'from_model': 'Account Payments'
            }
            self.env['detail.logs'].create(logs)
            self.env.cr.commit()

            raise ValidationError(e)

    def wa_history(self):
        return {
            'name': (_('WhatsApp History')),
            'domain': [('from_model', '=', 'Account Payments'), ('contact_name', '=', self.partner_id.id)],
            'view_type': 'form',
            'res_model': 'detail.logs',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def history_counter(self):
        self.history_count = len(self.env['detail.logs'].search([('from_model', '=', 'Account Payments'), ('contact_name', '=', self.partner_id.id)]))

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


class ResInventry(models.Model):
    _inherit = 'stock.picking'

    msg_count_pay = fields.Integer('Message Counter')
    msg_highlite = fields.Char('Message Highlight')
    message_sales = fields.Char('Message Payment')
    history_count = fields.Integer('History Counter', compute='history_counter')

    def send_msg(self):
        # print('xyz')

        report_id = self.env.ref('stock.action_report_delivery')
        if report_id:
            pdf, data = report_id.sudo()._render(self.id)
            pdf64 = base64.b64encode(pdf)
            attachment_invoice = self.env['ir.attachment'].create(
                {
                    # "name": f"{self.type_name} - {self.name}",
                    "name": self.display_name,
                    'type': 'binary',
                    "datas": pdf64
                }
            )

        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        inventory_check = self.env['ir.config_parameter'].sudo().get_param(
            'de_whatsapp_connector.inventory')

        if inventory_check:
            self.message_sales = f"""Hello {self.partner_id.name},\nPlease Acknowledge Attached {self.state} Report.\n
The {self.state} "{self.name}" Contain Following Information\n"""
            self.message_sales += f"""----------------------------\nShipping Date: {str(self.date)[:10]}\nProducts: {len(self.move_line_ids)}\n"""

            new_message = ''
            for product in self.move_line_ids:
                new_message += f"""----------------------------\nPrduct Name: {product.display_name}\nQty: {product.qty_done}\n"""

            self.message_sales += new_message + '----------------------------'

        else:
            self.message_sales = ''

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard.stock',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_contacts_to': [[6, 0, self.partner_id.ids]],
                            'default_whatsapp_account': credetionals.id,
                            'default_attatchments_whatsap': [[6, 0, [attachment_invoice.id]]],
                            'default_record_id': self.id,
                            'default_message': self.message_sales,
                            'default_model_name': str(self._inherit),
                            # 'default_contacts_to': 1,
                            },
                }

    def whatsapp_stock(self):
        try:
            cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
            credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

            if not credetionals:
                raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
            # else:
            #     self.name = credetionals.id

            if not self:
                raise UserError('You Have Not Selected Any Payments!')

            instance = credetionals.whatsapp_instance_id
            token = credetionals.whatsapp_token

            header = {
                'Content-type': 'application/json',
            }

            for order in self:

                contact = order.partner_id
                if not contact.country_id.phone_code:
                    raise UserError(f'"{contact.name}" Recipient does not contain Country. Select Country First!')

                signature_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.whatsapp_signature')

                inventory_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.inventory')

                if inventory_check:
                    order.message_sales = f"""Hello {order.partner_id.name},\nPlease Acknowledge Attached {order.state} Report.\n
The {order.state} "{order.name}" Contain Following Information\n"""
                    order.message_sales += f"""----------------------------\nShipping Date: {str(order.date)[:10]}\nProducts: {len(order.move_line_ids)}\n"""

                    new_message = ''
                    for product in order.move_line_ids:
                        new_message += f"""----------------------------\nPrduct Name: {product.display_name}\nQty: {product.qty_done}\n"""

                    order.message_sales += new_message + '----------------------------'

                else:
                    order.message_sales = f'Hello {contact.name},\nPlease Acknowledge Attached {order.display_name} Report. \n'

                if signature_check:
                    signature_str = ''
                    signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                    for signature in signature_list:
                        if signature:
                            signature_str += signature

                    order.message_sales += '\n \n--' + signature_str + '--'

                phone = str(contact.country_id.phone_code) + contact.mobile[-10:]

                if len(phone) < 11 or len(phone) > 13:
                    raise UserError(f'"{contact}" Might Have Wrong Phone Number!')

                url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"

                responce_status_code = 0
                data = json.dumps({"phone": phone, "body": order.message_sales})
                responce = requests.post(url, data, headers=header)
                responce_status_code = responce.status_code

                report = self.env.ref('stock.action_report_delivery').report_action(order)
                report_id = self.env.ref('stock.action_report_delivery')
                pdf, data = report_id.sudo()._render(order.id)
                pdf64 = base64.b64encode(pdf)
                attachment_id = self.env['ir.attachment'].create(
                    {
                        "name": f"{order.state}",
                        "datas": pdf64
                    }
                )

                url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
                json_response_file = 0

                decode_data = attachment_id.datas.decode('utf-8')
                docode_file = f"data:{attachment_id.mimetype};base64," + decode_data
                data_file = {
                    "phone": phone,
                    'filename': attachment_id.name,
                    "body": docode_file
                }
                response_file = requests.request("POST", url_files, json=data_file, headers={})
                json_response_file = response_file.status_code
                # print('Ending')

                if responce_status_code == 200 or json_response_file == 200:
                    # self.message_sent_id = json_responce['id']

                    order.write({
                        'msg_count_pay': order.msg_count_pay + 1,
                    })
                    p = self.env['res.partner'].search([('id', '=', contact.id)])
                    x = p.message_counter + 1
                    p.write({
                        'message_counter': x,
                        'message_highliter': f'Whatsapp Messages:{x}'
                    })

                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + order.message_sales,
                        'attachment_ids': [[6, 0, [attachment_id.id]]],
                        'model': 'stock.picking',
                        'res_id': order.id,
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

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Stock Picking'
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
                        'message_sucess': 'Error',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Stock Picking'
                    }
                    self.env['detail.logs'].create(logs)
                self.env.cr.commit()
            else:
                context = dict(self._context)
                context['message'] = 'Sucessful!'
                return self.message_wizard(context)

        except Exception as e:
            logs = {
                # 'sync_list_id': self.id,
                'sync_date': datetime.now(),
                'contact_name': contact.id,
                'account_used': credetionals.id,
                'message_sucess': 'Error',
                'files_attachted': [[6, 0, [attachment_id.id]]],
                'signature_att': 'Yes' if signature_check else 'No',
                'from_model': 'Stock Picking'
            }
            self.env['detail.logs'].create(logs)
            self.env.cr.commit()

            raise ValidationError(e)

    def wa_history(self):
        return {
            'name': (_('WhatsApp History')),
            'domain': [('from_model', '=', 'Stock Picking'), ('contact_name', '=', self.partner_id.id)],
            'view_type': 'form',
            'res_model': 'detail.logs',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def history_counter(self):
        self.history_count = len(self.env['detail.logs'].search([('from_model', '=', 'Stock Picking'), ('contact_name', '=', self.partner_id.id)]))

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


class ResPurchase(models.Model):
    _inherit = 'purchase.order'

    msg_count_pur = fields.Integer('Message Counter')
    msg_highlite = fields.Char('Message Highlight')
    message_sales = fields.Char('Message Purchase')
    history_count = fields.Integer('History Counter', compute='history_counter')

    def send_msg(self):
        # print('xyz')

        report_id = self.env.ref('purchase.action_report_purchase_order')
        if report_id:
            pdf, data = report_id.sudo()._render(self.id)
            pdf64 = base64.b64encode(pdf)
            attachment_invoice = self.env['ir.attachment'].create(
                {
                    # "name": f"{self.type_name} - {self.name}",
                    "name": self.display_name,
                    'type': 'binary',
                    "datas": pdf64
                }
            )

        cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
        credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

        purchase_check = self.env['ir.config_parameter'].sudo().get_param(
            'de_whatsapp_connector.purchase')

        if purchase_check:
            self.message_sales = f"""Hello {self.partner_id.name},\nPlease Acknowledge Attached {self.state} Report.\n
The {self.state} "{self.name}" Contain Following {len(self.order_line)} Products With Total Amount {self.amount_total}.\n"""
            new_message = ''
            for order in self.order_line:
                new_message += f"""----------------------------\nPrduct Name: {order.name}\nQty: {order.product_uom_qty}\nUnit Price: {order.price_unit}\nSubtotal: {order.price_subtotal}\n"""

            self.message_sales += new_message + '----------------------------'
        else:
            self.message_sales = ''

        return {'type': 'ir.actions.act_window',
                'name': _('Whatsapp Message'),
                'res_model': 'whatsapp.message.wizard.payments',
                'target': 'new',
                'view_mode': 'form',
                'view_type': 'form',
                'context': {'default_contacts_to': [[6, 0, self.partner_id.ids]],
                            'default_whatsapp_account': credetionals.id,
                            'default_attatchments_whatsap': [[6, 0, [attachment_invoice.id]]],
                            'default_record_id': self.id,
                            'default_message': self.message_sales,
                            'default_model_name': str(self._inherit),
                            },
                }

    def whatsapp_purchase(self):
        try:
            cre_id = self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_connector.select_account_whatsapp')
            credetionals = self.env['whatsapp.settings'].search([('id', '=', cre_id)])

            if not credetionals:
                raise UserError('You Have Not Selected Whatsapp Account or Forget to Save Creditionals!')
            # else:
            #     self.name = credetionals.id

            if not self:
                raise UserError('You Have Not Selected Any Payments!')

            instance = credetionals.whatsapp_instance_id
            token = credetionals.whatsapp_token

            header = {
                'Content-type': 'application/json',
            }

            for order in self:

                contact = order.partner_id
                if not contact.country_id.phone_code:
                    raise UserError(f'"{contact.name}" Recipient does not contain Country. Select Country First!')

                signature_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.whatsapp_signature')

                purchase_check = self.env['ir.config_parameter'].sudo().get_param(
                    'de_whatsapp_connector.purchase')

                if purchase_check:
                    order.message_sales = f"""Hello {order.partner_id.name},\nPlease Acknowledge Attached {order.state} Report.\n
The {order.state} "{order.name}" Contain Following {len(order.order_line)} Products With Total Amount {order.amount_total}.\n"""
                    new_message = ''
                    for order_l in self.order_line:
                        new_message += f"""----------------------------\nPrduct Name: {order_l.name}\nQty: {order_l.product_uom_qty}\nUnit Price: {order_l.price_unit}\nSubtotal: {order_l.price_subtotal}\n"""

                    order.message_sales += new_message + '----------------------------'
                else:
                    order.message_sales = f"Hello {order.partner_id.name},\nPlease Acknowledge Attached {order.state} Report."

                # message = f'Hello {contact.name},\nPlease Acknowledge Attached {order.display_name} Report.\n \n'

                if signature_check:
                    signature_str = ''
                    signature_list = re.findall("\>(.*?)\<", self.env.user.signature)
                    for signature in signature_list:
                        if signature:
                            signature_str += signature

                    order.message_sales += '\n\n--' + signature_str + '--'

                phone = str(contact.country_id.phone_code) + contact.mobile[-10:]

                if len(phone) < 11 or len(phone) > 13:
                    raise UserError(f'"{contact}" Might Have Wrong Phone Number!')

                url = f"https://eu38.chat-api.com/instance{instance}/sendMessage?token={token}"

                responce_status_code = 0
                data = json.dumps({"phone": phone, "body": order.message_sales})
                responce = requests.post(url, data, headers=header)
                responce_status_code = responce.status_code

                report = self.env.ref('purchase.action_report_purchase_order').report_action(order)
                report_id = self.env.ref('purchase.action_report_purchase_order')
                pdf, data = report_id.sudo()._render(order.id)
                pdf64 = base64.b64encode(pdf)
                attachment_id = self.env['ir.attachment'].create(
                    {
                        "name": f"{order.name}",
                        "datas": pdf64
                    }
                )

                url_files = f"https://eu38.chat-api.com/instance{instance}/sendFile?token={token}"
                json_response_file = 0

                decode_data = attachment_id.datas.decode('utf-8')
                docode_file = f"data:{attachment_id.mimetype};base64," + decode_data
                data_file = {
                    "phone": phone,
                    'filename': attachment_id.name,
                    "body": docode_file
                }
                response_file = requests.request("POST", url_files, json=data_file, headers={})
                json_response_file = response_file.status_code
                # print('Ending')

                if responce_status_code == 200 or json_response_file == 200:
                    # self.message_sent_id = json_responce['id']

                    order.write({
                        'msg_count_pur': order.msg_count_pur + 1,
                    })
                    p = self.env['res.partner'].search([('id', '=', contact.id)])
                    x = p.message_counter + 1
                    p.write({
                        'message_counter': x,
                        'message_highliter': f'Whatsapp Messages:{x}'
                    })

                    message = self.env['mail.message'].create({
                        'subject': 'Whatsapp Message',
                        'body': 'Whatsapp Message:\n' + order.message_sales,
                        'attachment_ids': [[6, 0, [attachment_id.id]]],
                        'model': 'purchase.order',
                        'res_id': order.id,
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

                    logs = {
                        # 'sync_list_id': self.id,
                        'sync_date': datetime.now(),
                        'contact_name': contact.id,
                        'account_used': credetionals.id,
                        'message_sucess': 'Sucessful',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Purchase'
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
                        'message_sucess': 'Error',
                        'files_attachted': [[6, 0, [attachment_id.id]]],
                        'signature_att': 'Yes' if signature_check else 'No',
                        'from_model': 'Purchase'
                    }
                    self.env['detail.logs'].create(logs)
                self.env.cr.commit()
            else:
                context = dict(self._context)
                context['message'] = 'Sucessful!'
                return self.message_wizard(context)

        except Exception as e:
            logs = {
                # 'sync_list_id': self.id,
                'sync_date': datetime.now(),
                'contact_name': contact.id,
                'account_used': credetionals.id,
                'message_sucess': 'Error',
                'files_attachted': [[6, 0, [attachment_id.id]]],
                'signature_att': 'Yes' if signature_check else 'No',
                'from_model': 'Purchase'
            }
            self.env['detail.logs'].create(logs)
            self.env.cr.commit()

            raise ValidationError(e)

    def wa_history(self):
        return {
            'name': (_('WhatsApp History')),
            'domain': [('from_model', '=', 'Purchase'), ('contact_name', '=', self.partner_id.id)],
            'view_type': 'form',
            'res_model': 'detail.logs',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def history_counter(self):
        self.history_count = len(self.env['detail.logs'].search([('from_model', '=', 'Purchase'), ('contact_name', '=', self.partner_id.id)]))

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


class BoxSettings(models.Model):
    _name = 'whatsapp.settings'

    name = fields.Char(string='Instance Name')
    whatsapp_instance_id = fields.Char(string='WhatsApp ID')
    whatsapp_token = fields.Char(string='WhatsApp Token')
    image = fields.Binary()

    def get_qr_code(self):
        # print('df')
        header = {
            'Content-type': 'application/json',
        }

        if not self.whatsapp_token and not self.name and not self.whatsapp_instance_id:
            raise UserError('Please Enter Creditionals First!')

        url = f"https://eu38.chat-api.com/instance{self.whatsapp_instance_id}/qr_code?token={self.whatsapp_token}"

        response = (requests.request("GET", url, headers=header))

        self.image = base64.b64encode(response.content)
        self.env.cr.commit()

    def test_connection(self):
        try:
            header = {
                'Content-type': 'application/json',
            }
            url = f"https://eu38.chat-api.com/instance{self.whatsapp_instance_id}/status?token={self.whatsapp_token}"
            response = (requests.request("GET", url, headers=header)).json()
            if response['accountStatus'] == 'authenticated':
                context = dict(self._context)
                context['message'] = 'Connection Successful!'
                return self.message_wizard(context)
            elif response['accountStatus'] == 'got qr code':
                self.get_qr_code()
                context = dict(self._context)
                context['message'] = 'Connection Successful!'
                return self.message_wizard(context)
        except:
            raise UserError('Check Whatsapp Crediontionals')

    def get_logout(self):
        header = {
            'Content-type': 'application/json',
        }
        url = f"https://eu38.chat-api.com/instance{self.whatsapp_instance_id}/logout?token={self.whatsapp_token}"

        responce = requests.post(url, headers=header)
        json_responce = responce.json()
        if responce.status_code == 200 and json_responce['result'] == 'Logout request sent to WhatsApp':
            context = dict(self._context)
            context['message'] = 'Logout request sent to WhatsApp!'
            return self.message_wizard(context)
        # response = (requests.request("POST", url, headers=header))
        # response = (requests.request("GET", url, headers=header))
        # response2 = requests.get(url, headers=header)
        # content = json.loads((response.content.decode('utf-8')))

        # print('checking status')

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
