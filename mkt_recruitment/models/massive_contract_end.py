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
    # employee_ids = fields.One2many('hr.employee', 'massive_contract_end_id', string='Verified employees')
    employee_ids = fields.Many2many('hr.employee', string='Verified employees')
    file_result = fields.Binary(string='Processed Employees', readonly=True)
    error_message = fields.Text(string='Errores de verificación')


    def employee_verification_xlsx(self):
        if not self.file_employees:
            raise UserError(_('No hay un archivo adjunto.'))
        self.reviewed = True
        decoded_file = base64.b64decode(self.file_employees)
        excel_file = io.BytesIO(decoded_file)
        wb = load_workbook(excel_file)
        ws = wb.active
        df = pd.read_excel(io.BytesIO(decoded_file))
        red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
        yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")
        error_rows = []
        for index, row in df.iterrows():
            nro_Doc = str(row['Nro_Doc']).strip()
            employees = self.env['hr.employee'].search([('identification_id', '=', nro_Doc)])
            if len(employees) == 0:
                ws[f'A{index + 2}'].fill = red_fill
                error_rows.append(row)
            elif len(employees) > 1:
                ws[f'A{index + 2}'].fill = yellow_fill
                error_rows.append(row)
                employees.write({'is_duplicated': True})
                self.write({'employee_ids': [(4, emp.id) for emp in employees]})
            else:
                self.write({'employee_ids': [(4, emp.id) for emp in employees]})
        output = io.BytesIO()
        df_filtered = pd.DataFrame(error_rows)
        with pd.ExcelWriter(output, engine='openpyxl') as writer:  
            df_filtered.to_excel(writer, index=False, sheet_name='Errores')
        output.seek(0)
        modified_file = base64.b64encode(output.read())
        self.file_result = modified_file  
        return {
            'effect': {
                'fadeout': 'fast',
                'message': _('Employees end. Processed file available.'),
                'type': 'rainbow_man',
            }
        }


    def massive_employee_terminations_xlsx(self):
        if not self.file_employees:
            raise UserError(_('No hay un archivo adjunto.'))
        self.reviewed = True
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
            motive = str(row['Motivo_Fin_Per_Lab_Id']).lstrip('0')
            employees = self.env['hr.employee'].search([('identification_id', '=', nro_Doc)])
            departure_reason = self.env['hr.departure.reason'].search([('motive_number', '=', motive)])
            if not departure_reason:
                raise UserError(_('El número de motivo de salida del DNI %s no esta registrado en el sistema.') % (nro_Doc))
            # Revizar si existe y en caso no que salte un UserError
            # Tambien debemos revizar una forma en la que no concidere las filas completamente en blancoo sea, si los tres campos estan vacios o por lo menos con el valor de una casilla vacia que podria ser 1.0?
            if len(employees) == 1:
                departure_wizard_employee_vals = {
                    'employee_id': employees.id,
                    'departure_reason_id': departure_reason.id,
                }
                departure_wizard_employee = self.env['hr.departure.wizard'].sudo().create(departure_wizard_employee_vals).sudo()
                departure_wizard_employee.with_context(toggle_active=True).action_departure_employees()
        return {
            'effect': {
                'fadeout': 'fast',
                'message': _('Employees end'),
                'type': 'rainbow_man',
            }
        }