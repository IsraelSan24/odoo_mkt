from odoo import models, fields

class ApplicantSetFieldsWizard(models.TransientModel):
    _name = "applicant.set.contract.fields.wizard"
    _description = "Set necessary fields to approve selected applicants."

    first_contract_start = fields.Date(string='First Contract Start Date')
    first_contract_end = fields.Date(string='First Contract End Date')
    salary_proposed = fields.Float(string="Proposed Salary")
    cost_center_id = fields.Many2one('cost.center', string='Cost Center')

    def action_confirm(self):
        active_ids = self.env.context.get('active_ids', [])
        applicants = self.env['hr.applicant'].browse(active_ids)

        for applicant in applicants:
            applicant.cost_center_id = self.cost_center_id if self.cost_center_id else False
            applicant.first_contract_start = self.first_contract_start if self.first_contract_start else False
            applicant.first_contract_end = self.first_contract_end if self.first_contract_end else False
            applicant.salary_proposed = self.salary_proposed if self.salary_proposed else False

        return {'type': 'ir.actions.act_window_close'}