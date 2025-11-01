from odoo import _, fields, models

class RecruitmentStage(models.Model):
    _inherit = 'hr.recruitment.stage'

    employee_stage = fields.Boolean(help='If checked, this stage is used to convert the record from applicant to employee',
                                    string='Employee stage')
    update_data = fields.Boolean(string='Update Data')
    access_portal = fields.Boolean(string='Access Portal')
    contact_merge = fields.Boolean(string='Contact Merge')
    # create_first_contract = fields.Boolean(string='Create First Contract')