from odoo import _, fields, models

class RecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    employee_stage = fields.Boolean(help='If checked, this stage is used to convert the record from applicant to employee',
                                    string='Employee stage')
