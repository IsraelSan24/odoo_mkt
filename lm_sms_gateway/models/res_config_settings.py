from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lm_user = fields.Char(string="LabsMobile User", config_parameter='lm_sms.user')
    lm_token = fields.Char(string="LabsMobile API Token", config_parameter='lm_sms.token')
    lm_tpoa_default = fields.Char(string="Remitente (TPOA) por defecto", config_parameter='lm_sms.tpoa')
    lm_base_url = fields.Char(string="URL API",
                              default="https://api.labsmobile.com/json/send",
                              config_parameter='lm_sms.base_url')
    lm_country_code = fields.Char(
        string="Prefijo país", default="51",
        config_parameter='lm_sms.country_code'
    )
    lm_force_country_code = fields.Boolean(
        string="Forzar prefijo país en todos los números",
        default=True,
        config_parameter='lm_sms.force_country_code'
    )