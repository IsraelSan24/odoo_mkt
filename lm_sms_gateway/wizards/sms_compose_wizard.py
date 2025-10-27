from odoo import api, fields, models, _
from odoo.exceptions import UserError

class LmSmsComposeWizard(models.TransientModel):
    _name = 'lm.sms.compose.wizard'
    _description = 'Enviar SMS (LabsMobile)'

    tpoa = fields.Char(string='Remitente (TPOA)')
    message = fields.Text(string='Mensaje', required=True)
    partner_ids = fields.Many2many('res.partner', string='Contactos')
    msisdn_preview = fields.Text(string='Destinatarios', readonly=True)

    @api.model
    def default_get(self, fields_list):
        vals = super().default_get(fields_list)
        active_model = self.env.context.get('active_model')
        active_ids = self.env.context.get('active_ids')
        msisdns = []
        if active_model == 'res.partner' and active_ids:
            for p in self.env[active_model].browse(active_ids):
                # Usa mobile o phone
                num = p.mobile or p.phone
                if num:
                    msisdns.append(''.join(ch for ch in num if ch.isdigit()))
        vals['msisdn_preview'] = '\n'.join(msisdns)
        return vals

    def action_send(self):
        self.ensure_one()
        if not self.message:
            raise UserError(_('Escribe un mensaje.'))
        # Recopilar MSISDNs de partner_ids o del preview
        msisdns = []
        for p in self.partner_ids:
            num = p.mobile or p.phone
            if num:
                msisdns.append(''.join(ch for ch in num if ch.isdigit()))
        if not msisdns and self.msisdn_preview:
            msisdns = [x.strip() for x in self.msisdn_preview.splitlines() if x.strip()]
        if not msisdns:
            raise UserError(_('No hay números destino.'))
        self.env['sms.gateway.labsmobile'].send_sms(msisdns, self.message, tpoa=self.tpoa)
        return {'type': 'ir.actions.client', 'tag': 'display_notification',
                'params': {'title': _('SMS enviado'), 'message': _('Se envió tu SMS a %s destinatario(s).') % len(msisdns), 'type': 'success'}}