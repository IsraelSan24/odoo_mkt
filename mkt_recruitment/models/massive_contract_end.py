from odoo import _, api, fields, models
from odoo.exceptions import UserError
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import pandas as pd
import base64
import io
import logging
_logger = logging.getLogger(__name__)

# update_types = [
#     ('subdiary','Subdiary'),
# ]

class MassiveContractEnd(models.Model):
    _name = 'massive.contract.end'
    _order = 'id desc'

    name = fields.Char(string='Name')
    file_employees = fields.Binary(string='Employees')
    reviewed = fields.Boolean(string='Is reviewed?', default=False)
    employee_ids = fields.One2many('hr.employee', 'massive_contract_end_id', string='Verified employees', context={'active_test': False})
    # employee_ids = fields.Many2many('hr.employee', string='Verified employees', domain=[(1, '=', 1)] )

    file_result = fields.Binary(string='Processed Employees', readonly=True)
    error_message = fields.Text(string='Errores de verificación')
    massive_termination_done = fields.Boolean(string="Massive Contract Done")
    

    def employee_verification_xlsx(self):
        if not self.file_employees:
            raise UserError(_('No hay un archivo adjunto.'))
        
        decoded_file = base64.b64decode(self.file_employees)
        df = pd.read_excel(io.BytesIO(decoded_file))

        self.error_message = ""
        error_rows = []
        employee_ids_to_add = []
        n_employees_ok = 0

        for index, row in df.iterrows():
            nro_Doc = str(row['Nro_Doc']).strip()
            employees = self.env['hr.employee'].search([('address_home_id.vat', '=', nro_Doc)])

            if not employees:
                error_rows.append(row)
                self.error_message += (_("- Empleado activo no encontrado: %s\n"% nro_Doc))


            elif len(employees) > 1:
                # error_rows.append(row)
                employees.write({'is_duplicated': True})
                # self.error_message += (_("- Empleado duplicado: %s\n"% nro_Doc))
                employee_ids_to_add += employees.ids
                n_employees_ok += len(employee_ids_to_add)

            else:
                n_employees_ok += 1
                employee_ids_to_add += employees.ids
                
            self.env['hr.employee'].browse(employee_ids_to_add).write({
                'massive_contract_end_id': self.id
            })

            # self.write({'employee_ids': [(4, emp_id) for emp_id in employee_ids_to_add]})


        self.reviewed = True
        df_not_founds = pd.DataFrame(error_rows)
        output = io.BytesIO()

        if len(df_not_founds) > 0:
            with pd.ExcelWriter(output, engine='openpyxl') as writer:  
                df_not_founds.to_excel(writer, index=False, sheet_name='Errores')

            output.seek(0)
            self.file_result = base64.b64encode(output.read())

        return {
            'effect': {
                'fadeout': 'slow',
                'message': _('Employees found: %s. Employees with errors: %s' % (n_employees_ok, len(df_not_founds))),
                'type': 'rainbow_man',
            }
        }


    def massive_employee_terminations_xlsx(self):
        if not self.file_employees:
            raise UserError(_('No hay un archivo adjunto.'))
        
        decoded_file = base64.b64decode(self.file_employees)
        excel_file = io.BytesIO(decoded_file)
        df = pd.read_excel(excel_file)

        for index, row in df.iterrows():
            if (not(row['Nro_Doc'])) :
                raise UserError(_('El número de DNI de alguna fila se encuentra vacio.'))
            
            if (not(row['Fecha_cese'])) or (not(row['Motivo_Fin_Per_Lab_Id'])):
                raise UserError(_('El la fila del DNI %s no se encuentra la fecha o el motivo.') % (str(row['Nro_Doc'])))
            
            nro_Doc = str(row['Nro_Doc'])
            date_end = row['Fecha_cese']
            motive = int(row['Motivo_Fin_Per_Lab_Id'])
            employees = self.env['hr.employee'].search([('address_home_id.vat', '=', nro_Doc)])
            departure_reason = self.env['hr.departure.reason'].search([('motive_number', '=', motive)])

            if not departure_reason:
                raise UserError(_('El número de motivo de salida del DNI %s no esta registrado en el sistema.') % (nro_Doc))
            
            # Tambien debemos revizar una forma en la que no concidere las filas completamente en blancoo sea, si los tres campos estan vacios o por lo menos con el valor de una casilla vacia que podria ser 1.0?
            if len(employees) == 1:
                departure_wizard_employee_vals = {
                    'employee_id': employees.id,
                    'departure_reason_id': departure_reason.id,
                    'departure_date': date_end,
                    'set_date_end': True,
                    'cancel_leaves': True,
                    'archive_allocation': True,
                    'archive_private_address': True,
                }
                departure_wizard_employee = self.env['hr.departure.wizard'].sudo().create(departure_wizard_employee_vals).sudo()
                departure_wizard_employee.with_context(toggle_active=True).action_departure_employees()

        self.massive_termination_done = True

        return {
            'effect': {
                'fadeout': 'fast',
                'message': _('Employees end'),
                'type': 'rainbow_man',
            }
        }

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('massive.contract.end') or _('New')
        return super(MassiveContractEnd, self).create(vals)