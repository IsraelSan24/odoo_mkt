from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ApplicantSetFieldsWizard(models.TransientModel):
    _name = "applicant.set.contract.fields.wizard"
    _description = "Set necessary fields to approve selected applicants."

    first_contract_start = fields.Date(string='First Contract Start Date')
    first_contract_end = fields.Date(string='First Contract End Date')
    salary_proposed = fields.Float(string="Proposed Salary")
    cost_center_id = fields.Many2one('cost.center', string='Cost Center')


    def _save_data(self):
        active_ids = self.env.context.get('active_ids', [])
        applicants = self.env['hr.applicant'].browse(active_ids)

        if not applicants:
            raise UserError(_("No applicants selected."))

        forbidden_status = {'rejected', 'approved'}
        supervision_status = set(applicants.mapped('supervision_data_approved') or [])

        if supervision_status.intersection(forbidden_status):
            _logger.info(f"\n\n\n{forbidden_status} - {supervision_status} - {supervision_status.intersection(forbidden_status)}\n\n\n")
            raise UserError(_("You can only modify contract data when request is pending."))

        # Aplica cambios con write() (más limpio y atómico)
        vals = {
            'cost_center_id': self.cost_center_id.id or False,
            'first_contract_start': self.first_contract_start or False,
            'first_contract_end': self.first_contract_end or False,
            'salary_proposed': self.salary_proposed or False,
        }
        applicants.write(vals)

        return applicants

    def action_save(self):
        self._save_data()
        
        return {'type': 'ir.actions.act_window_close'}
    

    def action_save_and_approve(self):
        applicants = self._save_data()
        applicants.action_approve_selected_applicants()

        return {'type': 'ir.actions.act_window_close'}