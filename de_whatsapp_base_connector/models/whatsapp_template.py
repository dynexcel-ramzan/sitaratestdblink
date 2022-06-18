# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging


from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WhatsappTemplate(models.Model):
    "Templates for sending Whatsapp Message"
    _name = "whatsapp.template"
    _inherit = ['mail.render.mixin']
    _description = 'Whatsapp Templates'
    _order = 'name'

    @api.model
    def default_get(self, fields):
        res = super(WhatsappTemplate, self).default_get(fields)
        if res.get('model'):
            res['model_id'] = self.env['ir.model']._get(res.pop('model')).id
        return res

    # description
    name = fields.Char('Name')
    model_id = fields.Many2one('ir.model', 'Applies to', help="The type of document this template can be used with")
    model = fields.Char('Related Document Model', related='model_id.model', index=True, store=True, readonly=True)
    subject = fields.Char('Subject', translate=True, help="Subject (placeholders may be used here)")
    whatsapp_from = fields.Char('From',
                             help="Sender address (placeholders may be used here). If not set, the default "
                                  "value will be the author's whatsapp alias if configured, or whatsapp address.")
    # recipients
    use_default_to = fields.Boolean(
        'Default recipients',
        help="Default recipients of the record:\n"
             "- partner (using id on a partner or the partner_id field) OR\n"
             )
    whasatpp_to = fields.Char('To (Whatsapp)', help="Comma-separated recipient addresses (placeholders may be used here)")
    partner_to = fields.Char('To (Partners)',
                             help="Comma-separated ids of recipient partners (placeholders may be used here)")
    whatsapp_cc = fields.Char('Cc', help="Carbon copy recipients (placeholders may be used here)")
    reply_to = fields.Char('Reply-To', help="Preferred response address (placeholders may be used here)")
    # content
    body_html = fields.Text('Body', translate=True, sanitize=False)
    attachment_ids = fields.Many2many('ir.attachment', 'whatsapp_template_attachment_rel', 'email_template_id',
                                      'attachment_id', 'Attachments',
                                      help="You may attach files to this template, to be added to all "
                                           "Message created from this template")
    report_name = fields.Char('Report Filename', translate=True,
                              help="Name to use for the generated report file (may contain placeholders)\n"
                                   "The extension can be omitted and will then come from the report type.")
    report_template = fields.Many2one('ir.actions.report', 'Optional report to print and attach')
    # options
  
    scheduled_date = fields.Char('Scheduled Date', help="If set, the queue manager will send the message after the date. If not set, the message will be send as soon as possible. Jinja2 placeholders may be used.")
    auto_delete = fields.Boolean(
        'Auto Delete', default=True,
        help="This option permanently removes any track of message after it's been sent, including from the Technical menu in the Settings, in order to preserve storage space of your Odoo database.")
    # contextual action
    ref_ir_act_window = fields.Many2one('ir.actions.act_window', 'Sidebar action', readonly=True, copy=False,
                                        help="Sidebar action to make this template available on records "
                                             "of the related document model")

    def unlink(self):
        self.unlink_action()
        return super(WhatsappTemplate, self).unlink()

    @api.returns('self', lambda value: value.id)
    def copy(self, default=None):
        default = dict(default or {},
                       name=_("%s (copy)", self.name))
        return super(WhatsappTemplate, self).copy(default=default)

    def unlink_action(self):
        for template in self:
            if template.ref_ir_act_window:
                template.ref_ir_act_window.unlink()
        return True

    def create_action(self):
        ActWindow = self.env['ir.actions.act_window']
        view = self.env.ref('de_whatsapp_base_connector.whatsapp_compose_message_wizard_form')

        for template in self:
            button_name = _('Send Whatsapp Message')
            action = ActWindow.create({
                'name': button_name,
                'type': 'ir.actions.act_window',
                'res_model': 'whatsapp.compose.message',
                'context': "{'default_composition_mode': 'mass_whatsapp', 'default_template_id' : %d, 'default_use_template': True}" % (template.id),
                'view_mode': 'form,tree',
                'view_id': view.id,
                'target': 'new',
                'binding_model_id': template.model_id.id,
            })
            template.write({'ref_ir_act_window': action.id})

        return True

    # ------------------------------------------------------------
    # MESSAGE/whatsapp VALUES GENERATION
    # ------------------------------------------------------------

    def generate_recipients(self, results, res_ids):
        """Generates the recipients of the template. Default values can ben generated
        instead of the template values if requested by template or context.
        can be transformed into partners if requested
        in the context. """
        self.ensure_one()

        if self.use_default_to or self._context.get('tpl_force_default_to'):
            records = self.env[self.model].browse(res_ids).sudo()
            default_recipients = records._message_get_default_recipients()
            for res_id, recipients in default_recipients.items():
                results[res_id].pop('partner_to', None)
                results[res_id].update(recipients)

        records_company = None
        if self._context.get('tpl_partners_only') and self.model and results and 'company_id' in self.env[self.model]._fields:
            records = self.env[self.model].browse(results.keys()).read(['company_id'])
            records_company = {rec['id']: (rec['company_id'][0] if rec['company_id'] else None) for rec in records}

        for res_id, values in results.items():
#             partner_ids = values.get('partner_ids', list())
            if self._context.get('tpl_partners_only'):
                whatsapp = tools.email_split(values.pop('whatsapp_to', '')) + tools.email_split(values.pop('whatsapp_cc', ''))
                Partner = self.env['res.partner']
                if records_company:
                    Partner = Partner.with_context(default_company_id=records_company[res_id])
                for message in whatsapp:
                    partner = Partner.find_or_create(message)
#                     partner_ids.append(partner.id)
            partner_to = values.pop('partner_to', '')
            if partner_to:
                # placeholders could generate '', 3, 2 due to some empty field values
                tpl_partner_ids = [int(pid) for pid in partner_to.split(',') if pid]
#                 partner_ids += self.env['res.partner'].sudo().browse(tpl_partner_ids).exists().ids
#             results[res_id]['partner_ids'] = partner_ids
        return results

   
    # ------------------------------------------------------------
    # Whatsapp
    # ------------------------------------------------------------
    
    def generate_whatsapp(self, res_ids, fields):
        """Generates an message from the template for given the given model based on
        records given by res_ids.

        :param res_id: id of the record to use for rendering the template (model
                       is taken from template definition)
        :returns: a dict containing all relevant fields for creating a new
                   entry, with one extra key ``attachments``, in the
                  format [(report_name, data)] where data is base64 encoded.
        """
        self.ensure_one()
        multi_mode = True
        if isinstance(res_ids, int):
            res_ids = [res_ids]
            multi_mode = False

        results = dict()
        for lang, (template, template_res_ids) in self._classify_per_lang(res_ids).items():
            for field in fields:
                template = template.with_context(safe=(field == 'subject'))
                generated_field_values = template._render_field(
                    field, template_res_ids,
                    post_process=(field == 'body_html')
                )
                for res_id, field_value in generated_field_values.items():
                    results.setdefault(res_id, dict())[field] = field_value
            # compute recipients
            if any(field in fields for field in ['whatsapp_to', 'partner_to', 'whatsapp_cc']):
                results = template.generate_recipients(results, template_res_ids)
            # update values for all res_ids
            for res_id in template_res_ids:
                values = results[res_id]
                if values.get('body_html'):
                    values['body'] = tools.html_sanitize(values['body_html'])
                # technical settings
                values.update(
                    auto_delete=template.auto_delete,
                    model=template.model,
                    res_id=res_id or False,
                    attachment_ids=[attach.id for attach in template.attachment_ids],
                )

            # Add report in attachments: generate once for all template_res_ids
            if template.report_template:
                for res_id in template_res_ids:
                    attachments = []
                    report_name = self._render_field('report_name', [res_id])[res_id]
                    report = template.report_template
                    report_service = report.report_name

                    if report.report_type in ['qweb-html', 'qweb-pdf']:
                        result, format = report._render_qweb_pdf([res_id])
                    else:
                        res = report._render([res_id])
                        if not res:
                            raise UserError(_('Unsupported report type %s found.', report.report_type))
                        result, format = res

                    # TODO in trunk, change return format to binary to match message_post expected format
                    result = base64.b64encode(result)
                    if not report_name:
                        report_name = 'report.' + report_service
                    ext = "." + format
                    if not report_name.endswith(ext):
                        report_name += ext
                    attachments.append((report_name, result))
                    results[res_id]['attachments'] = attachments

        return multi_mode and results or results[res_ids[0]]

    
    
    

    def _send_check_access(self, res_ids):
        records = self.env[self.model].browse(res_ids)
        records.check_access_rights('read')
        records.check_access_rule('read')

