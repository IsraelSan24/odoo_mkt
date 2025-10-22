# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning

class HrApplicant(models.Model):
    _inherit = 'hr.applicant'

    def _is_blacklisted_vat(self):
        Partner = self.env['res.partner']
        for rec in self:
            vat = rec.vat or rec.partner_id.vat
            if vat and Partner.search_count([('vat', '=', vat), ('blacklist', '=', True)]):
                return True
        return False

    @api.model
    def create(self, vals):
        # No bloquea en create, solo en cambio de etapa
        return super().create(vals)

    def write(self, vals):
        # Si se intenta mover a stage_id == 2, verificar blacklist
        move_to_stage2 = 'stage_id' in vals and int(vals['stage_id']) == 2
        force_ok = self.env.context.get('force_blacklist_continue')
        if move_to_stage2 and not force_ok:
            for rec in self:
                if rec._is_blacklisted_vat():
                    # Abrir wizard de confirmación (RedirectWarning con acción del wizard)
                    action = self.env.ref('mkt_supervision.action_applicant_blacklist_confirm_wizard').id
                    msg = _("Este postulante coincide con un contacto en la lista negra.\n"
                            "¿Desea continuar moviendo la postulación a esta etapa?")
                    # El botón del wizard permitirá continuar (setea el contexto) o cancelar.
                    raise RedirectWarning(msg, action, _('Revisar y continuar'))
        return super().write(vals)

    # Método utilitario para completar el paso con contexto 'force_blacklist_continue'
    def force_move_to_stage(self, stage_id):
        # Llama write con bandera para no re-disparar el bloqueo
        self.with_context(force_blacklist_continue=True).write({'stage_id': stage_id})
        return True
