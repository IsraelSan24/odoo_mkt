from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class ApplicantSetFieldsWizard(models.TransientModel):
    _name = "applicant.set.contract.fields.wizard"
    _description = "Set necessary fields to approve selected applicants."

    first_contract_start = fields.Date(string=_('First Contract Start Date'))
    first_contract_end = fields.Date(string=_('First Contract End Date'))
    salary_proposed = fields.Float(string=_("Proposed Salary"))
    cost_center_id = fields.Many2one('cost.center', string=_('Cost Center'))
    work_type = fields.Selection([
        ('week_end', 'Fin de Semana'),
        ('fix_without_mobility', 'Fijo sin Movilidad'),
        ('fix_with_mobility', 'Fijo con Movilidad'),
        ],
        string=_('Work Type'),
        default='fix_without_mobility')
    company_id = fields.Many2one('res.company', string='Compañía', default=lambda self: self.env.company)


    @api.model
    def _default_parent_id(self):
        current_employee = self.env['hr.employee'].search([('address_home_id', '=', self.env.user.partner_id.id)], limit=1) 
        return current_employee or False
    
    parent_id = fields.Many2one('hr.employee', 'Jefe Directo', domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", default=_default_parent_id)


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
            'work_type': self.work_type or False,
            'parent_id': self.parent_id or False,
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
    