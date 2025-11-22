import calendar
from datetime import datetime, timedelta

from odoo import models, fields, _
from odoo.tools import date_utils
from odoo.exceptions import ValidationError

class AttendanceTrackingReport(models.TransientModel):
    _name = 'attendance.tracking.report'
    _description = 'Asistencias y Ausencias Mensual'
    _inherit = ['report.formats']

    month = fields.Selection(
        [(str(i), str(i)) for i in range(1, 13)],
        string='Mes', required=True
    )
    year = fields.Char(
        string='Año', required=True,
        default=lambda self: str(datetime.now().year)
    )

    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')

    def _get_file_name(self, function_name, file_name=False):
        name = _('Reporte Asistencia Ausencia %s-%s') % (self.month, self.year)
        dic = super(AttendanceTrackingReport, self)._get_file_name(
            function_name,
            file_name=name
        )
        return dic

    def _get_my_subordinates_and_me(self):
        """
        Obtiene el empleado actual y todos sus subordinados recursivamente.
        Retorna una lista de IDs de empleados.
        """
        my_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if not my_employee:
            raise ValidationError(_("No hay un empleado vinculado al usuario actual."))
        
        # Incluimos al empleado actual
        all_employees = my_employee
        to_check = my_employee
        
        # Buscamos recursivamente todos los subordinados
        while to_check:
            children = self.env['hr.employee'].search([('parent_id', 'in', to_check.ids)])
            to_check = children - all_employees
            all_employees |= to_check

        return all_employees.ids

    def _get_datas_report_xlsx(self, workbook):
        """
        Genera la hoja de cálculo con:
        - Columnas: DNI, Nombre, Día1–DíaN, Totales verticales.
        - Las primeras 3 filas: 
            * Fila 1 (0-based): Mes Año (centrado sobre las columnas de días).
            * Fila 2: Día de la semana (S, D, L, M, X, J, V).
            * Fila 3: Día numérico (1, 2, 3, …).
        - Filas siguientes: un empleado por fila.
        - Luego, columnas fijas para totales (vertical rotated text).
        """

        mes = int(self.month)
        anio = int(self.year)
        first_day = datetime(anio, mes, 1).date()
        month_range = calendar.monthrange(anio, mes) 
        num_days = month_range[1]
        last_day = datetime(anio, mes, num_days).date()

        sheet_name = _('Asistencias %s-%s') % (self.month, self.year)
        ws = workbook.add_worksheet(sheet_name)
        ws.set_zoom(80)

        # --- Definición de anchos de columna
        ws.set_column(0, 0, 12)  # Col A: DNI
        ws.set_column(1, 1, 20)  # Col B: Nombre
        for col in range(2, 2 + num_days):
            ws.set_column(col, col, 3)  # cada día muy angosto
        for col in range(2 + num_days, 2 + num_days + 9):
            ws.set_column(col, col, 10)  # columnas de totales

        # --- Formatos
        header_center = workbook.add_format({
            'font_color': '#FFFFFF', 'bg_color': '#4F81BD',
            'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True
        })
        header_center_merged = workbook.add_format({
            'font_color': '#FFFFFF', 'bg_color': '#4F81BD',
            'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True
        })
        header_day = workbook.add_format({
            'font_color': '#FFFFFF', 'bg_color': '#4F81BD',
            'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        data_center = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        data_center_gray = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'border': 1,
            'bg_color': '#D9D9D9'
        })
        header_vertical = workbook.add_format({
            'font_color': '#FFFFFF', 'bg_color': '#4F81BD',
            'align': 'center', 'valign': 'bottom', 'border': 1,
            'rotation': 90, 'bold': True
        })

        # --- Escribir encabezados
        title = _('MES DE %s %s') % (calendar.month_name[mes].upper(), anio)
        if num_days > 0:
            ws.merge_range(0, 2, 0, 2 + num_days - 1, title, header_center_merged)
        ws.merge_range(0, 0, 2, 0, _('DNI'), header_center)
        ws.merge_range(0, 1, 2, 1, _('NOMBRE'), header_center)

        # Fila 1: Día de la semana
        for day in range(1, num_days + 1):
            fecha = datetime(anio, mes, day).date()
            weekday = fecha.weekday()
            siglas = ['L', 'M', 'X', 'J', 'V', 'S', 'D']
            letra = siglas[weekday]
            ws.write(1, 2 + (day - 1), letra, header_day)

        # Fila 2: Día numérico
        for day in range(1, num_days + 1):
            ws.write(2, 2 + (day - 1), day, header_day)

        # Encabezados de totales
        totales = [
            _('DIAS TRABAJADOS'),
            _('DIAS VACACIONES'),
            _('DIAS SUBSIDIO MATERNIDAD'),
            _('LICENCIA PATERNIDAD'),
            _('DESCANSO MÉDICO MENOR 20 DÍAS'),
            _('DESCANSO MÉDICO MAYOR 20 DÍAS'),
            _('FERIADOS'),
            _('DIAS NO LABORADOS'),
            _('LICENCIA SIN GOCE DE HABER'),
        ]
        inicio_tot = 2 + num_days
        for idx, txt in enumerate(totales):
            ws.write(2, inicio_tot + idx, txt, header_vertical)

        # --- Pre-carga de datos
        all_employee_ids = self._get_my_subordinates_and_me()
        employees = self._get_query_employees(all_employee_ids)
        attends = self._get_query_attendance(first_day, last_day, all_employee_ids)
        attend_set = set((r[0], r[1]) for r in attends)

        leaves_raw = self._get_query_leaves(first_day, last_day, all_employee_ids)
        leaves_map = {}
        for rec in leaves_raw:
            emp = rec['emp_id']
            ini = rec['inicio']
            fin = rec['fin']
            sig = rec['sigla'] or ''
            current = max(ini, first_day)
            end_range = min(fin, last_day)
            delta = (end_range - current).days
            for d in range(delta + 1):
                dia = current + timedelta(days=d)
                leaves_map[(emp, dia)] = sig

        # --- Escribir filas de datos
        row = 3
        for emp in employees:
            emp_id = emp['emp_id']
            dni = emp['dni'] or ''
            nombre = emp['nombre'] or ''
            ws.write(row, 0, dni, data_center)
            ws.write(row, 1, nombre, data_center)

            tot_ausencias = 0
            tot_vacaciones = 0
            tot_subsidio = 0
            tot_paternidad = 0
            tot_medico_menor = 0
            tot_medico_mayor = 0
            tot_feriados = 0
            tot_no_laborados = 0
            tot_sin_goce = 0

            for dia in range(1, num_days + 1):
                fecha = datetime(anio, mes, dia).date()
                col = 2 + (dia - 1)

                if fecha.weekday() in (5, 6):
                    ws.write(row, col, 'H', data_center_gray)
                    tot_no_laborados += 1
                    continue

                key = (emp_id, fecha)
                if key in leaves_map:
                    sigla = leaves_map[key]
                    ws.write(row, col, sigla, data_center)
                    if sigla.upper() == 'V':
                        tot_vacaciones += 1
                    elif sigla.upper() == 'S':
                        tot_subsidio += 1
                    elif sigla.upper() == 'P':
                        tot_paternidad += 1
                    elif sigla.upper() == 'M':
                        tot_medico_menor += 1
                    elif sigla.upper() == 'N':
                        tot_medico_mayor += 1
                    elif sigla.upper() == 'F':
                        tot_feriados += 1
                    elif sigla.upper() == 'L':
                        tot_sin_goce += 1
                    else:
                        tot_ausencias += 1
                    continue

                if (emp_id, fecha) in attend_set:
                    ws.write(row, col, 'A', data_center)
                else:
                    ws.write(row, col, '', data_center)
                    tot_no_laborados += 1

            dias_trabajados = num_days - tot_ausencias - tot_vacaciones - tot_subsidio \
                              - tot_paternidad - tot_medico_menor - tot_medico_mayor \
                              - tot_feriados - tot_no_laborados - tot_sin_goce
            tot_values = [
                dias_trabajados,
                tot_vacaciones,
                tot_subsidio,
                tot_paternidad,
                tot_medico_menor,
                tot_medico_mayor,
                tot_feriados,
                tot_no_laborados,
                tot_sin_goce,
            ]
            for idx, val in enumerate(tot_values):
                ws.write(row, inicio_tot + idx, val, data_center)

            row += 1
    
    def _get_query_employees(self, employee_ids):
        query_emp = """
            SELECT he.id AS emp_id, rp.vat AS dni, rp.name AS nombre
            FROM hr_employee he
            JOIN res_users ru ON ru.id = he.user_id
            JOIN res_partner rp ON rp.id = ru.partner_id
            WHERE he.active = True AND he.id = ANY(%s)
            ORDER BY rp.name
        """
        self.env.cr.execute(query_emp, (employee_ids,))
        return self.env.cr.dictfetchall()
        
    def _get_query_attendance(self, first_day, last_day, employee_ids):
        query_att = """
            WITH attendance_data AS (
                SELECT
                    at.employee_id AS emp_id,
                    (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS fecha
                FROM hr_attendance at
                WHERE (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date BETWEEN %s AND %s
                  AND at.check_in IS NOT NULL
                  AND at.employee_id = ANY(%s)
                GROUP BY at.employee_id, (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date
            )
            SELECT emp_id, fecha FROM attendance_data
        """
        self.env.cr.execute(query_att, (first_day, last_day, employee_ids,))
        return self.env.cr.fetchall()
        
    def _get_query_leaves(self, first_day, last_day, employee_ids):
        query_leave = """
            SELECT hl.employee_id AS emp_id,
                   (hl.date_from AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS inicio,
                   (hl.date_to   AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS fin,
                   hlt.sigla AS sigla
            FROM hr_leave hl
            JOIN hr_leave_type hlt ON hlt.id = hl.holiday_status_id
            WHERE hl.state = 'validate'
              AND (hl.date_from AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date <= %s
              AND (hl.date_to   AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date >= %s
              AND hl.employee_id = ANY(%s)
        """
        self.env.cr.execute(query_leave, (last_day, first_day, employee_ids,))
        return self.env.cr.dictfetchall()
    
    def action_generate_tareo_sheet(self):
        """
        Crea un registro persistente (attendance.tareo.sheet) con las mismas
        asistencias/ausencias que se usan para el XLSX, pero editable.
        Ahora incluye al usuario actual.
        """
        self.ensure_one()

        mes = int(self.month)
        anio = int(self.year)
        first_day = datetime(anio, mes, 1).date()
        num_days = calendar.monthrange(anio, mes)[1]
        last_day = datetime(anio, mes, num_days).date()

        # Incluir al usuario actual y sus subordinados
        all_employee_ids = self._get_my_subordinates_and_me()
        employees = self._get_query_employees(all_employee_ids)
        attends = self._get_query_attendance(first_day, last_day, all_employee_ids)
        attend_set = set((r[0], r[1]) for r in attends)

        leaves_raw = self._get_query_leaves(first_day, last_day, all_employee_ids)
        leaves_map = {}
        for rec in leaves_raw:
            emp = rec['emp_id']
            ini = rec['inicio']
            fin = rec['fin']
            sig = rec['sigla'] or ''
            current = max(ini, first_day)
            end_range = min(fin, last_day)
            for d in range((end_range - current).days + 1):
                dia = current + timedelta(days=d)
                leaves_map[(emp, dia)] = sig

        # Construimos líneas
        line_vals = []
        for emp in employees:
            emp_id = emp['emp_id']
            vals_line = {
                'employee_id': emp_id,
                'dni': emp['dni'],
                'employee_name': emp['nombre'],
            }

            for day in range(1, num_days + 1):
                fecha = datetime(anio, mes, day).date()
                field_name = 'day_%02d' % day
                value = ''

                if fecha.weekday() in (5, 6):
                    value = 'H'
                else:
                    key = (emp_id, fecha)
                    if key in leaves_map:
                        value = leaves_map[key]
                    elif key in attend_set:
                        value = 'A'
                    else:
                        value = ''

                vals_line[field_name] = value

            line_vals.append((0, 0, vals_line))

        sheet = self.env['attendance.tareo.sheet'].create({
            'company_id': self.env.company.id,
            'responsible_id': self.env.user.id,
            'month': self.month,
            'year': self.year,
            'date_from': first_day,
            'date_to': last_day,
            'line_ids': line_vals,
        })

        return {
            'type': 'ir.actions.act_window',
            'name': _('Tareo %s-%s') % (self.month, self.year),
            'res_model': 'attendance.tareo.sheet',
            'res_id': sheet.id,
            'view_mode': 'form',
            'target': 'current',
        }