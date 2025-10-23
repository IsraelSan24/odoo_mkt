from odoo import models

class ResPartner(models.Model):
    _inherit = 'res.partner'

    def action_open_lm_sms_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Enviar SMS',
            'res_model': 'lm.sms.compose.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_model': 'res.partner',
                'active_ids': self.ids,
            }
        }
