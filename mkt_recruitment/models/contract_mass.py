from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta

contract_modes = [
    ('renovation', 'Renovation'),
    ('new_employee', 'New employee'),
]

states = [
    ('draft', 'Draft'),
    ('generated', 'Contracts generated'),
]

mode_modes = [
    ('manual', 'Manual'),
    ('auto', 'Auto'),
]

job_modes = [
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
    cost_center_id = fields.Many2one(comodel_name='cost.center',required=True, string='Cost center')
    employee_ids = fields.Many2many(comodel_name="hr.employee", relation="contract_mass_employee_rel", string="Employee")
    renew_employee_ids = fields.Many2many(comodel_name="hr.employee",required=True, relation="contract_mass_renew_employee_rel", string="Employee", domain="[('contract_id', '!=', False),('contract_id.state','=','open')]")
    renew_contracts_ids = fields.Many2many(comodel_name='hr.contract', relation="contract_mass_renew_contracts_rel", string='Created contracts')
    contract_type_id = fields.Many2one(comodel_name="hr.contract.type", string="Contract Type")
    mode = fields.Selection(selection=contract_modes, required=True, default='renovation', string='New or Renewed')
    # wage_mode = fields.Selection(selection=wage_modes, default='manual', string='Wage mode')
    mode_mode = fields.Selection(selection=mode_modes, default='auto', string='Manual or automatic')
    wage = fields.Float(string='Wage')
    job_mode = fields.Selection(selection=job_modes, default='auto', string='Job mode')
    job_id = fields.Many2one(comodel_name='hr.job', string='Job')
    date_start = fields.Date(default=fields.Date.today, string='Contract date start')
    date_end = fields.Date(default=default_date_end, string='Contract date end')
    renewed_months = fields.Integer(default=1, string='Months to renew')
    hr_responsible_id = fields.Many2one(comodel_name='res.users', string='HR responsible')
    campaign = fields.Char(string='Campaign')
    state = fields.Selection(selection=states, default='draft', string='State')
    last_contract_ids = fields.Many2many(comodel_name='hr.contract', compute='_compute_last_contracts', string='Last contracts', store=True)
    province_id = fields.Many2one(comodel_name='res.province', required=True, string='Manual or automatic')


    # Solo debe aparecer ste boton en el ultimo etado que ensi es el segundo
    def button_update_contracts(self):
        for rec in self.renew_contracts_ids:
            rec.write_data()


    # Solo debe aparecer ste boton en el ultimo etado que ensi es el segundo
    def button_send_contracts(self):
        for rec in self.renew_contracts_ids:
            rec.is_sended = True


    @api.onchange('cost_center_id')
    def change_cost_center(self):
        if self.cost_center_id:
            employees = self.env['hr.employee'].search([('cost_center_id','=',self.cost_center_id.id),('contract_id', '=', False)])
            renew_employees = self.env['hr.employee'].search([('cost_center_id','=',self.cost_center_id.id),('contract_id', '!=', False),('contract_id.state','=','open'),('address_home_id.province_id.id','=',self.province_id.id)])
            self.write({'employee_ids': [(5, 0, 0)] + [(4, emp.id) for emp in employees]})
            self.write({'renew_employee_ids': [(5, 0, 0)] + [(4, emp.id) for emp in renew_employees]})


    @api.depends('renew_employee_ids')
    def _compute_last_contracts(self):
        for record in self:
            last_contracts = []
            for employee in record.renew_employee_ids:
                last_contract = self.env['hr.contract'].search([
                    ('employee_id', '=', employee.id),
                    ('state', '=', 'open')
                ], order='date_start desc', limit=1)
                if last_contract:
                    last_contracts.append((4, last_contract.id))

            if last_contracts:
                record.write({'last_contract_ids': last_contracts})


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
            self.state = 'generated'


    def create_renewed_contract(self):
        if self.mode == 'renovation':
            for employee in self.renew_employee_ids:
                contract_employee = self.env['hr.contract'].search([('employee_id','=',employee.id),('state','=','open')], order='date_start desc', limit=1)
                employee_wage = contract_employee.wage
                employee_contract_type = contract_employee.contract_type_id
                employee_last_date_end = contract_employee.date_end
                new_date_start = employee_last_date_end + relativedelta(days=1)
                values = {
                    'employee_id': employee.id,
                    'date_start': new_date_start if self.mode_mode == 'auto' else self.date_start,
                    'date_end': (new_date_start + relativedelta(months=1) - relativedelta(days=new_date_start.day)) if self.mode_mode == 'auto' else self.date_end,
                    'contract_type_id': self.contract_type_id.id if self.mode_mode == 'manual' else employee_contract_type.id,
                    'wage': self.wage if self.mode_mode == 'manual' else employee_wage,
                    'structure_type_id': 1,
                    'is_renovation': True,
                    'department_id': employee.department_id.id,
                    'job_id': employee.job_id.id,
                }
                new_contract = self.env['hr.contract'].sudo().create(values)
                self.write({'renew_contracts_ids': [(4, new_contract.id)]})
                new_contract.write_data() 
                new_contract._compute_contract_duration()
            self.state = 'generated'


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('contract.mass') or _('New')
        return super(ContractMass, self).create(vals)