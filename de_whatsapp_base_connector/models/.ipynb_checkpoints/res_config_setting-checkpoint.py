from odoo import models, fields, api, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_signature = fields.Boolean('User Signature')

    @api.model
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param('de_whatsapp_base_connector.whatsapp_signature', self.whatsapp_signature)
        return param


    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            whatsapp_signature=True if self.env['ir.config_parameter'].sudo().get_param('de_whatsapp_base_connector.whatsapp_signature') == 'True' else False,
            )
        return res
