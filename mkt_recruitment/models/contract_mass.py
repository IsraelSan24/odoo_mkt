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

    active = fields.Boolean(default=True)
    name = fields.Char(copy=False, required=True, default=lambda self: _('New'), string='Name')
    employee_ids = fields.Many2many(comodel_name="hr.employee", relation="contract_mass_employee_rel", string="Employee", domain="['&', ('contract_id', '=', False), ('active', '=', True)]")
    contracts_ids = fields.One2many(comodel_name='hr.contract', inverse_name='massive_new_contracts_id', string='Created new contracts')
    renew_employee_ids = fields.Many2many(comodel_name="hr.employee", relation="contract_mass_renew_employee_rel", string="Employee")
    renew_contracts_ids = fields.One2many(comodel_name='hr.contract', inverse_name='massive_renew_contracts_id', string='Created renewed contracts')
    contract_type_id = fields.Many2one(comodel_name="hr.contract.type", string="Contract Type")
    mode = fields.Selection(selection=contract_modes, required=True, default='new_employee', string='New or Renewed')
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
    employees_with_other_cc = fields.Many2many(comodel_name='hr.employee', relation='employees_with_other_cc_rel', string="Employees with other cost center", store=True, readonly=True)
    employees_with_previous_contracts = fields.Many2many(comodel_name='hr.employee', relation='employees_with_previous_contracts_rel', string="Employees with previous contracts", store=True, readonly=True)
    # campo de texto donde el usuario pega los DNIs / VATs
    identifiers_input = fields.Text(string="Identifiers (one per line or comma separated)",
                                    help="Paste one identifier per line or separate them by commas/semicolons.")
    identifiers_not_found = fields.Text(string="Identifiers not found", readonly=True, store=True,
                                        help="Identifiers that were not found in the system.")
                                        

    def button_update_contracts(self):
        self.ensure_one()
        if self.mode == 'renovation':
            for rec in self.renew_contracts_ids:
                rec.write_data()
        elif self.mode == 'new_employee':
            new_values = {
                key: value for key, value in {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'wage': self.wage,
                'contract_type_id': self.contract_type_id.id,
                }.items() if value
            }
            self.contracts_ids.write(new_values)

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
                ], order='date_start desc', limit=1)
                if last_contract:
                    last_contracts.append(last_contract.id)

            record.last_contract_ids = [(6, 0, last_contracts)]

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
        self.ensure_one()
        if self.mode == 'renovation':
            for employee in self.renew_employee_ids:
                contract_employee = self.env['hr.contract'].search([('employee_id','=',employee.id)], order='date_start desc', limit=1)

                if not contract_employee:
                    raise UserError(_("No contract found for employee %s") % employee.name)

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

    def action_print_renewed_contracts(self):
        if not self.renew_contracts_ids:
            raise UserError(_("No renewed contracts found to print"))
        
        if len(self.renew_contracts_ids) > 1:
            return self.env['contract.zip.wizard'].with_context(active_ids=self.renew_contracts_ids.ids).create({}).action_generate_zip_contracts()
        else:
            return self.env.ref('mkt_recruitment.report_contract_action').report_action(self.renew_contracts_ids)

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
        # employees = self.employee_ids.search([('identification_id', 'in', id_list)])
        employees = hr_employee.search([('identification_id', 'in', id_list), ('active', '=', True), ('contract_id', '=', False)])
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

    @api.onchange('employee_ids', 'validate_cost_center_id', 'employees_with_other_cc')
    def process_identifiers(self):
        """Busca employees por identificadores y reemplaza employee_ids."""
        self.ensure_one()

        if self.mode == 'new_employee':
            id_list, missing, found_values, found_ids = self._get_ids()
            
            if not id_list:
                self.employee_ids = False
                self.identifiers_not_found = False
                self.employees_with_previous_contracts = False
                return {
                    "type_message": "danger",
                    "message": _("No identifiers provided or all identifiers are invalid.")
                }
            
            if missing:
                self.employees_with_previous_contracts = self.env['hr.employee'].search([('identification_id', 'in', missing), ('active', '=', True)])  
                self.identifiers_not_found = "\n".join(sorted(list(set(missing) - set(self.employees_with_previous_contracts.mapped('identification_id')))))
            else:
                self.identifiers_not_found = False
                self.employees_with_previous_contracts = False

            # Reemplazamos la lista Many2many: (6, 0, ids)
            self.employee_ids = [(6, 0, found_ids)] # carga para el usuario también

            #####################
            # Validar centros de costo si se seleccionó uno
            emp_with_validate_cc = []
            emp_without_validate_cc = []

            if self.validate_cost_center_id:
                
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

            # Notificación al usuario desde el wizard
            return self._message_notif(id_list, missing, found_values, emp_with_validate_cc, emp_without_validate_cc)

    def _message_notif(self, id_list, missing, found_values, emp_with_validate_cc, emp_without_validate_cc):
        """Genera un mensaje de notificación para el usuario dependiendo de las combinaciones."""
        if not id_list:
            return {
                    "type_message": "danger",
                    "message": _("No identifiers provided or all identifiers are invalid.")
                }  

        elif not found_values:
            return {
                "type_message": "danger",
                "message": _("No employees found for the provided identifiers.")
            }
        else:
            if len(found_values) == len(id_list):
                if not emp_without_validate_cc:
                    return {
                        "type_message": "success",
                        "message": _("All identifiers found and all employees have the same cost center.")
                    }
                elif not emp_with_validate_cc:
                    return {
                        "type_message": "danger",
                        "message": _("All identifiers found but no employees have the selected cost center. Check errors page ⚠.")
                    }
                else:
                    return {
                        "type_message": "warning",
                        "message": _("All identifiers found but %s have different cost centers. Check errors page ⚠.") % len(emp_without_validate_cc)
                    }
            else:
                if not emp_without_validate_cc:
                    return {
                        "type_message": "warning",
                        "message": _("Some identifiers not found: %s.\nAll found employees have the same cost center. Check errors page ⚠.") % len(missing)
                    }
                elif not emp_with_validate_cc:
                    return {
                        "type_message": "danger",
                        "message": _("Some identifiers not found: %s.\nAll found employees don't have the selected cost center. Check errors page ⚠.") % len(missing)
                    }
                else:
                    return {
                        "type_message": "warning",
                        "message": _("Some identifiers not found: %s.\nEmployees with other cost center: %s. Check errors page ⚠.") % (len(missing), len(emp_without_validate_cc))
                    }

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
                          'employees_with_other_cc', 'identifiers_input', 'identifiers_not_found', 'employees_with_previous_contracts']
            for field in new_fields:
                self[field] = False

    @api.constrains('wage')
    def _check_wage(self):
        """Verifica que el salario sea mayor a 0."""
        for rec in self:
            if rec.wage <= 0.0 and rec.mode == 'new_employee':
                raise ValidationError(_("The wage must be greater than 0."))
    
    def toggle_active(self):
        '''Propaga el archivado desde el contrato masivo a los contratos individuales'''
        res = super(ContractMass, self).toggle_active()
        for rec in self:
            all_related_contracts = self.env['hr.contract'].with_context(active_test=False).search([
                '|', ('massive_new_contracts_id', '=', rec.id), ('massive_renew_contracts_id', '=', rec.id)
            ])
            if all_related_contracts:
                all_related_contracts.write({'active': rec.active})

        return res