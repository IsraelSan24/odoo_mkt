# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class ApplicantBlacklistConfirmWizard(models.TransientModel):
    _name = 'applicant.blacklist.confirm.wizard'
    _description = 'Confirmar cambio de etapa con blacklist'

    applicant_id = fields.Many2one('hr.applicant', required=True, ondelete='cascade')
    target_stage_id = fields.Many2one('hr.recruitment.stage', required=True)
    note = fields.Text(readonly=True, default=lambda self: _(
        "Este postulante coincide con un contacto en la lista negra.\n"
        "Si continúa, el proceso seguirá bajo su responsabilidad."
    ))

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get('active_id')
        vals = self.env.context.get('vals') or {}
        if active_id:
            res['applicant_id'] = active_id
        if 'stage_id' in vals:
            res['target_stage_id'] = vals['stage_id']
        return res

    def action_continue(self):
        self.ensure_one()
        self.applicant_id.force_move_to_stage(self.target_stage_id.id)
        return {'type': 'ir.actions.act_window_close'}

    def action_cancel(self):
        return {'type': 'ir.actions.act_window_close'}
