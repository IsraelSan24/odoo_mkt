from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
import re

contract_modes = [
    ('new_employee', 'New Contracts'),
    ('renovation', 'Renovation'),
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
    employee_ids = fields.Many2many(comodel_name="hr.employee", relation="contract_mass_employee_rel", string="Employee", domain="[('contract_id', '=', False)]")
    contracts_ids = fields.One2many(comodel_name='hr.contract', inverse_name='massive_new_contracts_id', string='Created new contracts')
    renew_employee_ids = fields.Many2many(comodel_name="hr.employee", relation="contract_mass_renew_employee_rel", string="Employee", domain="[('contract_id', '!=', False),('contract_id.state','=','open')]")
    renew_contracts_ids = fields.One2many(comodel_name='hr.contract', inverse_name='massive_renew_contracts_id', string='Created renewed contracts')
    contract_type_id = fields.Many2one(comodel_name="hr.contract.type", string="Contract Type")
    mode = fields.Selection(selection=contract_modes, required=True, default='renovation', string='New or Renewed')
    # wage_mode = fields.Selection(selection=wage_modes, default='manual', string='Wage mode')
    mode_mode = fields.Selection(selection=mode_modes, default='auto', string='Manual or automatic')
    wage = fields.Float(string='Wage', default=False)
    job_mode = fields.Selection(selection=job_modes, default='auto', string='Job mode')
    job_id = fields.Many2one(comodel_name='hr.job', string='Job')
    date_start = fields.Date(default=fields.Date.today, string='Contract date start')
    date_end = fields.Date(default=default_date_end, string='Contract date end')
    renewed_months = fields.Integer(default=1, string='Months to renew')
    hr_responsible_id = fields.Many2one(comodel_name='res.users', string='HR responsible')
    campaign = fields.Char(string='Campaign')
    state = fields.Selection(selection=states, default='draft', string='State')
    last_contract_ids = fields.Many2many(comodel_name='hr.contract', compute='_compute_last_contracts', string='Last contracts', store=True)
    province_id = fields.Boolean(default=True, required=True, string='Is Lima?')
    # validate_cost_center = fields.Selection(selection=lambda self: self._get_cost_center(), string="Cost center to validate")
    validate_cost_center_id = fields.Many2one(comodel_name='cost.center', string="Cost center to validate")
    employees_with_other_cc = fields.Many2many(comodel_name='hr.employee', string="Employees with other cost center", store=True, readonly=True)
    # campo de texto donde el usuario pega los DNIs / VATs
    identifiers_input = fields.Text(string="Identifiers (one per line or comma separated)",
                                    help="Paste one identifier per line or separate them by commas/semicolons.")
    identifiers_not_found = fields.Text(string="Identifiers not found", readonly=True, store=True,
                                        help="Identifiers that were not found in the system.")
                                        

    # Solo debe aparecer ste boton en el ultimo etado que ensi es el segundo
    def button_update_contracts(self):
        for rec in self.renew_contracts_ids:
            rec.write_data()

    # Solo debe aparecer ste boton en el ultimo etado que ensi es el segundo
    def button_send_contracts(self):
        if self.mode == 'renovation':
            for rec in self.renew_contracts_ids:
                rec.is_sended = True
        elif self.mode == 'new_employee':
            for rec in self.contracts_ids:
                rec.is_sended = True

    def button_unsend_contracts(self):
        if self.mode == 'renovation':
            for rec in self.renew_contracts_ids:
                rec.is_sended = False
        elif self.mode == 'new_employee':
            for rec in self.contracts_ids:
                rec.is_sended = False

    @api.onchange('province_id')
    def change_province_id(self):
        if self.province_id:
            employees = self.env['hr.employee'].search([('contract_id', '=', False)])
            if self.province_id == True:
                renew_employees = self.env['hr.employee'].search([('contract_id', '!=', False),('contract_id.state','=','open'),('address_home_id.province_id.name','=','Lima')])
            else:
                renew_employees = self.env['hr.employee'].search([('contract_id', '!=', False),('contract_id.state','=','open'),('address_home_id.province_id.name','!=','Lima')])
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
                    'structure_type_id': 1, # employee
                    'resource_calendar_id': 1, # 48 work hours per week
                    'contract_type_id': self.contract_type_id.id,
                    # 'hr_responsible_id': self.hr_responsible_id.id,
                    'is_renovation': False,
                }
                new_contract = self.env['hr.contract'].sudo().create(values)
                self.write({'contracts_ids': [(4, new_contract.id)]})
                new_contract.write_data() 
                new_contract._compute_contract_duration()
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
                    'date_end': (new_date_start + relativedelta(months=self.renewed_months) - relativedelta(days=new_date_start.day)) if self.mode_mode == 'auto' else self.date_end,
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
    
    def _parse_identifiers(self, text):
        '''
        Normaliza el texto y devuelve lista de identificadores (strings)
        '''
        if not text:
            return []
        
        # split por nueva línea, coma o punto y coma
        parts = re.split(r'[\r\n,;]+', text)

        ids = []
        for part in parts:
            strip_part = part.strip()
            if not strip_part:
                continue
            # limpia caracteres no alfanuméricos (salva letras y números)
            strip_part_clean = re.sub(r'[^A-Za-z0-9]', '', strip_part)
            if strip_part_clean:
                ids.append(strip_part_clean)
                
        # elimino duplicados manteniendo orden
        seen = set()
        result = []
        for id in ids:
            low = id.upper()   # para comparación insensible a mayúsculas
            if low not in seen:
                seen.add(low)
                result.append(id)
        return result

    def _get_ids(self):
        """Devuelve una lista de identificadores únicos de los empleados."""
        self.ensure_one()
                
        id_list = self._parse_identifiers(self.identifiers_input)

        if not id_list:
            return [], [], [], []

        hr_employee = self.env['hr.employee']
        found_emps = hr_employee.browse()

        # Buscar en cada campo y unir resultados
        employees = hr_employee.search([('identification_id', 'in', id_list)])
        found_emps |= employees # Eliminamos duplicados
        found_ids = found_emps.ids # ids de empleados encontrados

        # Calcular identificadores (no ids) encontrados para notificación
        found_values = set()

        if found_emps:
            # mapped puede devolver None si el campo no existe para algunos records
            try:
                vals = found_emps.mapped('identification_id')
                found_values.update([str(v).upper() for v in vals if v])
            except Exception:
                return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Error while processing identifiers'),
                    'message': _("There's an error while processing identifiers. Please check the format."),
                    'type': 'warning',
                    'sticky': False,
                    }
                }
            
        # missing = los que quedaron en id_list y no están en found_values
        missing = [v for v in id_list if v.upper() not in found_values]

        return (id_list, missing, found_values, found_ids)

    @api.onchange('employee_ids', 'validate_cost_center_id')
    def process_identifiers(self):
        """Busca employees por identificadores y reemplaza employee_ids."""
        self.ensure_one()

        if self.mode == 'new_employee':
            id_list, missing, found_values, found_ids = self._get_ids()
            
            if not id_list:
                self.employee_ids = False
                return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Nothing to import'),
                    'message': _('Please paste valid identifiers into the text box.'),
                    'type': 'warning',
                    'sticky': False,
                    }
                }

            # Reemplazamos la lista Many2many: (6, 0, ids)
            # self.write({'employee_ids': [(6, 0, found_ids)]})
            self.employee_ids = [(6, 0, found_ids)]
            # self.employees_with_other_cc = [(6, 0, found_ids)]

            # Notificación al usuario
            message = _("%d identifier(s) processed. %d employee(s) found.") % (len(id_list), len(found_ids))
            if missing:
                self.identifiers_not_found = "\n".join(missing)
                message += " " + _("Not found: %s") % (", ".join(missing[:10]) + ("..." if len(missing) > 10 else ""))

            #####################
            # Validar centros de costo si se seleccionó uno
            if self.validate_cost_center_id:
                emp_with_validate_cc = []
                emp_without_validate_cc = []
                
                for emp in self.employee_ids:
                    if self.validate_cost_center_id.id == emp.cost_center_id.id:
                        emp_with_validate_cc.append(emp.id)
                    else:
                        emp_without_validate_cc.append(emp.id)
                
                self.employee_ids = [(6, 0, emp_with_validate_cc)]
                self.employees_with_other_cc = [(6, 0, emp_without_validate_cc)]
            else:
                self.employees_with_other_cc = [(6, 0, [])]

            #####################

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Import finished'),
                    'message': message,
                    'type': 'success' if found_ids else 'warning',
                    'sticky': False,
                }
            }

    # def button_validate_cost_center(self):
    #     """Valida el centro de costo seleccionado."""
    #     if not self.validate_cost_center_id:
    #         raise UserError(_("Please select a cost center to validate."))
        
    #     emp_cost_centers_id = self.employee_ids.mapped('cost_center_id')
    #     emp_cost_centers = [cost_center_id if cost_center_id else "Sin CC" for cost_center_id in emp_cost_centers_id.mapped('id')]

    #     unique_emp_cost_centers = list(set(emp_cost_centers))

    #     # All employees have a defined cost center
    #     if emp_cost_centers:
            
    #         if len(unique_emp_cost_centers) == 1:
    #             if unique_emp_cost_centers[0] == self.validate_cost_center_id.id:
    #                 return {
    #                 'type': 'ir.actions.client',
    #                 'tag': 'display_notification',
    #                 'params': {
    #                     'title': _('Cost Center Validation'),
    #                     'message': _("All employees have the same cost center: _%s_.") % self.validate_cost_center_id.id,
    #                     'type': 'success',
    #                     'sticky': True,
    #                     }
    #                 }
                
    #             return {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'title': _('Cost Center Validation'),
    #                 'message': _("All employees have a different cost center: _%s_") % unique_emp_cost_centers[0],
    #                 'type': 'warning',
    #                 'sticky': True,
    #                 }
    #             }

    #         elif len(unique_emp_cost_centers) > 1:
    #             other_cost_centers = [cc for cc in unique_emp_cost_centers if cc != self.validate_cost_center_id.id]

    #             self.employees_with_other_cc = self.employee_ids.browse(other_cost_centers)
    #             return {
    #                 'type': 'ir.actions.client',
    #                 'tag': 'display_notification',
    #                 'params': {
    #                     'title': _('Cost Center Validation'),
    #                     'message': _("Employees have different cost centers: _%s_") % ", ".join(str(cc) for cc in other_cost_centers),
    #                     'type': 'warning',
    #                     'sticky': True,
    #                     'tag': 'reload'
    #                 }
    #             }

    #     else:
    #         return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'title': _('Cost Center Validation'),
    #             'message': f"No employees with any cost center found.",
    #             'type': 'warning',
    #             'sticky': False,
    #             }
    #         }

    def action_open_identifiers_wizard(self):
        self.ensure_one()
        return {
            'name': _('Introduce IDs'),
            'type': 'ir.actions.act_window',
            'res_model': 'contract.mass.identifiers.wizard',
            'view_mode': 'form',
            'view_id': self.env.ref('mkt_recruitment.identifiers_wizard_form_view').id,
            'target': 'new',  # importante: abre modal
            'context': {
                'default_identifiers_input': '',
                'active_model': self._name,
                'active_id': self.id
            },
        }

    @api.onchange('mode')
    def _onchange_mode(self):
        """Limpia los campos relacionados al modo cuando se cambia de un modo a otro."""
        if self.mode == 'new_employee':
            renovation_fields = ['renew_employee_ids', 'contract_type_id', 'wage', 'date_start', 'date_end', 'renewed_months', 'last_contract_ids', 'identifiers_not_found']
            for field in renovation_fields:
                self[field] = False
            self.mode_mode = 'auto' 

        elif self.mode == 'renovation':
            new_fields = ['validate_cost_center_id', 'contract_type_id', 'wage', 'date_start', 'date_end', 'employee_ids', 'contracts_ids', 
                          'employees_with_other_cc', 'identifiers_not_found', 'identifiers_input', 'identifiers_not_found']
            for field in new_fields:
                self[field] = False

    @api.constrains('wage')
    def _check_wage(self):
        """Verifica que el salario sea mayor a 0."""
        for rec in self:
            if rec.wage <= 0.0 and rec.mode == 'new_employee':
                raise ValidationError(_("The wage must be greater than 0."))