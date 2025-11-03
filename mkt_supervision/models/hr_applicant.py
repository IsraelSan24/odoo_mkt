# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import RedirectWarning, ValidationError, UserError, MissingError
import logging

_logger = logging.getLogger(__name__)

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


    def action_approve_selected_applicants(self):
        for record in self:
            
            if record.stage_id.id != 2:
                raise UserError(_(f"You can approve only selected applicants."))
            
            # Verificar campos requeridos
            missing_fields = []

            if not record.cost_center_id:
                missing_fields.append("Cost Center")
            if not record.salary_proposed:
                missing_fields.append("Salary Proposed")
            if not record.first_contract_start:
                missing_fields.append("First Contract Start")
            if not record.first_contract_end:
                missing_fields.append("First Contract End")

            if missing_fields:
                raise UserError(_(
                    "Some fields are required to approve applicant %s:\n→ %s"
                ) % (record.partner_name or record.name, "\n→ ".join(missing_fields)))

            record.write({
                'stage_id': self.env.ref('hr_recruitment.stage_job4').id,  # Mejor usar xml_id que hardcodear 4
                'supervision_data_sent': True,
                'selected_applicant_approved': True,
                'supervision_data_approved': 'pending',
            })
            

    def action_open_set_fields_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Set First Contract Fields',
            'res_model': 'applicant.set.contract.fields.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids}
        }