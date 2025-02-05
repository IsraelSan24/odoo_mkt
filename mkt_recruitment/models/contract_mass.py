from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta

contract_mode = [
    ('renovation', 'Renovation'),
    ('new_employee', 'New employee'),
]

state = [
    ('draft', 'Draft'),
    ('generated', 'Contracts generated'),
]

wage_mode = [
    ('manual', 'Manual'),
    ('auto', 'Auto'),
]

job_mode = [
    ('manual', 'Manual'),
    ('auto', 'Auto'),
]

def default_date_end(self):
    return fields.Date.today() + relativedelta(months=3)

class ContractMass(models.Model):
    _name = "contract.mass"
    _description = 'Massive Contract'
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(copy=False, required=True, default=lambda self: _('New'), string='Name')
    employee_ids = fields.Many2many(comodel_name="hr.employee", string="Employee")
    contract_type_id = fields.Many2one(comodel_name="hr.contract.type", string="Contract Type")
    mode = fields.Selection(selection=contract_mode, required=True, default='renovation', string='New or Renewed')
    wage_mode = fields.Selection(selection=wage_mode, default='manual', string='Wage mode')
    wage = fields.Float(string='Wage')
    job_mode = fields.Selection(selection=job_mode, default='manual', string='Job mode')
    job_id = fields.Many2one(comodel_name='hr.job', string='Job')
    date_start = fields.Date(default=fields.Date.today, string='Contract date start')
    date_end = fields.Date(default=default_date_end, string='Contract date end')
    renewed_months = fields.Integer(default=1, string='Months to renew')
    hr_responsible_id = fields.Many2one(comodel_name='res.users', string='HR responsible')
    campaign = fields.Char(string='Campaign')
    state = fields.Selection(selection=state, default='draft', string='State')
    last_contract_ids = fields.Many2many(comodel_name='hr.contract', compute='_compute_last_contracts', string='Last contracts', store=True)


    @api.depends('employee_ids')
    def _compute_last_contracts(self):
        for rec in self:
            last_contracts = self.env['hr.contract']
            for employee in rec.employee_ids:
                last_contract = employee.contract_ids.sorted(key=lambda r: r.date_start, reverse=True)[:1]
                last_contracts |= last_contract
            rec.last_contract_ids = last_contracts


    def create_contract_to_new_employee(self):
        if self.mode == 'new_employee':
            for employee in self.employee_ids:
                values = {
                    'employee_id': employee.id,
                    'department_id': employee.department_id.id or employee.applicant_id.department_id.id,
                    'job_id': employee.job_id.id or employee.applicant_id.job_id.id,
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    # 'contract_months': str(relativedelta(self.date_end, self.date_start).years * 12 + relativedelta(self.date_end, self.date_start).months) + _(' months.'),
                    'wage': self.wage,
                    'contract_type_id': self.contract_type_id.id,
                    'hr_responsible_id': self.hr_responsible_id.id,
                    'is_renovation': False,
                }
                new_contract = self.env['hr.contract'].sudo().create(values)
                new_contract._onchange_subtract_date()
            self.state = 'generated'


    def create_renewed_contract(self):
        if self.mode == 'renovation':
            for employee in self.employee_ids:
                contract_employee = self.env['hr.contract'].search([('employee_id','=',employee.id)], order='date_start desc', limit=1)
                employee_wage = contract_employee.wage
                employee_last_date_end = contract_employee.date_end
                new_date_start = employee_last_date_end + relativedelta(days=1)
                the_job = employee.job_id.id if self.job_mode == 'auto' else self.job_id.id
                values = {
                    'employee_id': employee.id,
                    'department_id': employee.department_id.id or employee.applicant_id.department_id.id,
                    'job_id': the_job,
                    'date_start': new_date_start,
                    'date_end': new_date_start + relativedelta(months=1) - relativedelta(days=new_date_start.day),
                    # 'contract_months': str(self.renewed_months) + _(' months.'),
                    'wage': self.wage if self.wage_mode == 'manual' else employee_wage,
                    'contract_type_id': self.contract_type_id.id,
                    'hr_responsible_id': self.hr_responsible_id.id,
                    'is_renovation': True,
                }
                new_contract = self.env['hr.contract'].sudo().create(values)
                new_contract._onchange_subtract_date() 
            self.state = 'generated'


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.mass') or _('New')
        return super(ContractMass, self).create(vals)
