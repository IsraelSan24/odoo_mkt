from odoo import api, fields, models, tools, _

class ApplicantContract(models.Model):
    _name = 'applicant.contract'
    _description = 'Applicant Contract'
    _auto = False
    _order = 'is_under_contract'

    name = fields.Char(readonly=True, string='Contract Name')
    applicant = fields.Char(readonly=True, string='Applicant')
    cost_center_id = fields.Many2one(comodel_name='cost.center', readonly=True, string='Cost center')
    partner_id = fields.Many2one(comodel_name='res.partner', readonly=True, string='Customer')
    date_hired = fields.Date(readonly=True, string='Hire Date')
    date_start = fields.Date(readonly=True, string='Start Date')
    date_end = fields.Date(readonly=True, string='End Date')
    employee_id = fields.Many2one(comodel_name='hr.employee', readonly=True, string='Employee')
    is_under_contract = fields.Boolean(readonly=True, string='Is Currently Under Contract')
    state = fields.Selection([
        ('draft', 'New'),
        ('open', 'Running'),
        ('close', 'Expired'),
        ('cancel', 'Cancelled'),
    ], readonly=True, string='Status')
    wage = fields.Float(readonly=True, string='Wage', help="Employee's monthly gross wage.")
    under_contract_state = fields.Selection([
        ('done', 'Under Contract'),
        ('blocked', 'Not under Contract'),
    ], compute='_compute_under_contract_state', string='Contractual Status')
    stage_id = fields.Many2one(comodel_name='hr.recruitment.stage', readonly=True, string='Recruitment Stage')
    signed_by_employer = fields.Boolean(readonly=True, string='Signed by employer')
    hr_responsible_contract_id = fields.Many2one(comodel_name='res.users', string='Approved by')


    @api.depends('is_under_contract')
    def _compute_under_contract_state(self):
        for history in self:
            history.under_contract_state = 'done' if history.is_under_contract else 'blocked'


    def init(self):
        tools.drop_view_if_exists(self._cr, 'applicant_contract')
        self._cr.execute("""
            CREATE or REPLACE view applicant_contract AS (
                SELECT
                    hch.id AS id,
                    hch.employee_id AS employee_id,
                    ha.name AS applicant,
                    he.cost_center_id AS cost_center_id,
                    cc.partner_id AS partner_id,
                    hch.date_hired AS date_hired,
                    hch.name AS name,
                    hch.date_start AS date_start,
                    hch.date_end AS date_end,
                    hch.wage AS wage,
                    hch.state AS state,
                    hch.is_under_contract AS is_under_contract,
                    ha.stage_id AS stage_id,
                    hc.signed_by_employer AS signed_by_employer,
                    ha.hr_responsible_contract_id AS hr_responsible_contract_id
                FROM hr_contract_history AS hch
                    LEFT JOIN hr_employee AS he ON he.id=hch.employee_id
                    RIGHT JOIN hr_applicant AS ha ON ha.emp_id=he.id
                    LEFT JOIN hr_recruitment_stage AS hrs ON hrs.id=ha.stage_id
                    LEFT JOIN hr_contract AS hc ON hc.id=hch.contract_id
                    LEFT JOIN cost_center AS cc ON cc.id=he.cost_center_id
                WHERE hrs.name IN ('Contract Proposal','Contract Signed')
                ORDER BY ha.id DESC, hch.is_under_contract DESC
            )
        """)