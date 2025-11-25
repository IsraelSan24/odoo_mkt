# -*- coding: utf-8 -*-
from odoo import _, models, fields, api
from odoo.exceptions import UserError
from datetime import date, timedelta

class AttendanceReportAll(models.TransientModel):
    _name = 'attendance.report.all'
    _description = 'Attendance Report (All Employees)'
    _inherit = ['report.formats']

    date_from = fields.Date(string="Start Date", required=True, default=lambda s: date.today().replace(day=1))
    date_to = fields.Date(string="End Date", required=True, default=lambda s: date.today())

    def action_print_xlsx(self):
        if self.date_from > self.date_to:
            raise UserError(_('Start Date must be before or equal to End Date.'))
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')

    def _get_file_name(self, function_name, file_name=False):
        return super()._get_file_name(function_name, file_name=_('Attendance Report (All)'))

    # ---------------------------
    # Helpers
    # ---------------------------
    def _iter_dates(self, dfrom, dto):
        cur = dfrom
        while cur <= dto:
            yield cur
            cur += timedelta(days=1)

    def _month_name_es(self, m):
        # en mayúsculas como en tu imagen
        return {
            1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL',
            5: 'MAYO', 6: 'JUNIO', 7: 'JULIO', 8: 'AGOSTO',
            9: 'SETIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE',
        }[m]

    def _dow_letter(self, d):
        # L M X J V S D (X para miércoles)
        return {0: 'L', 1: 'M', 2: 'X', 3: 'J', 4: 'V', 5: 'S', 6: 'D'}[d.weekday()]

    def _get_employee_cost_center(self, emp):
        # Ajusta/añade aquí el nombre real de tu campo si es distinto
        candidates = [
            'cost_center_id',
            'x_cost_center_id',
            'x_studio_centro_de_costo',
            'analytic_account_id',
            'department_id',  # fallback común
        ]
        for fname in candidates:
            if fname in emp._fields:
                val = emp[fname]
                if not val:
                    continue
                # Many2one -> recordset; Char -> string
                return getattr(val, 'display_name', False) or getattr(val, 'name', False) or (val if isinstance(val, str) else '')
        return ''

    def _get_planilla_label(self, emp):
        is_back_office = False
        if 'is_back_office' in emp._fields:
            is_back_office = bool(emp.is_back_office)
        return 'OFICINA' if is_back_office else 'ACTIVIDADES'

    def _get_hire_dates_map(self, employee_ids):
        """Primera fecha de inicio de contrato por empleado."""
        if not employee_ids:
            return {}
        self._cr.execute("""
            SELECT employee_id, MIN(date_start) AS hire_date
            FROM hr_contract
            WHERE employee_id = ANY(%(employee_ids)s)
              AND date_start IS NOT NULL
            GROUP BY employee_id
        """, {'employee_ids': employee_ids})
        return {r['employee_id']: r['hire_date'] for r in self._cr.dictfetchall()}

    def _get_attendance_map(self, employee_ids):
        """Mapa (employee_id, date_local) -> {'in': time|None, 'out': time|None}."""
        if not employee_ids or not self.date_from or not self.date_to:
            return {}

        tz = 'America/Lima'
        params = {
            'tz': tz,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'employee_ids': employee_ids,
        }

        query = """
            WITH ad AS (
                SELECT
                    at.employee_id,
                    (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s)::date AS date_local,
                    MIN(at.check_in  AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s) AS check_in_local,
                    MAX(at.check_out AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s) AS check_out_local
                FROM hr_attendance at
                JOIN hr_employee he ON he.id = at.employee_id
                WHERE he.active = TRUE
                  AND at.employee_id = ANY(%(employee_ids)s)
                  AND (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s)::date BETWEEN %(date_from)s AND %(date_to)s
                GROUP BY at.employee_id, (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s)::date
            )
            SELECT
                employee_id,
                date_local,
                check_in_local::time AS check_in,
                CASE
                    WHEN check_out_local IS NOT NULL
                     AND check_out_local::date = date_local
                     AND check_out_local::time < time '23:00:00'
                    THEN check_out_local::time
                END AS check_out
            FROM ad
        """
        self._cr.execute(query, params)
        out = {}
        for r in self._cr.dictfetchall():
            out[(r['employee_id'], r['date_local'])] = {
                'in': r['check_in'],
                'out': r['check_out'],
            }
        return out
    

    def _get_employee_ids_with_attendance(self):
        self.ensure_one()
        if not self.date_from or not self.date_to:
            return []

        tz = 'America/Lima'
        params = {'tz': tz, 'date_from': self.date_from, 'date_to': self.date_to}

        self._cr.execute("""
            SELECT DISTINCT at.employee_id
            FROM hr_attendance at
            JOIN hr_employee he ON he.id = at.employee_id
            WHERE he.active = TRUE
            AND (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s)::date
                BETWEEN %(date_from)s AND %(date_to)s
        """, params)
        return [r[0] for r in self._cr.fetchall()]

    # ---------------------------
    # XLSX
    # ---------------------------
    def _get_datas_report_xlsx(self, workbook):
        self.ensure_one()
        if self.date_from > self.date_to:
            raise UserError(_('Start Date must be before or equal to End Date.'))

        ws = workbook.add_worksheet(_('ASISTENCIA'))

        ws.set_zoom(80)
        ws.set_row(0, 20)  # MES
        ws.set_row(1, 22)  # Día del mes (YA NO ROTADO)
        ws.set_row(2, 22)  # Día semana (YA NO ROTADO)

        # Columnas fijas
        ws.set_column(0, 0, 14)  # DNI
        ws.set_column(1, 1, 55)  # APELLIDOS Y NOMBRES
        ws.set_column(2, 2, 14)  # FECHA DE INGRESO
        ws.set_column(3, 3, 18)  # CENTRO DE COSTO
        ws.set_column(4, 4, 14)  # PLANILLA
        ws.set_column(5, 5, 18)  # OBSERVACIONES

        # ====== Estilos ======
        st_month = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#BFBFBF', 'border': 1
        })
        st_fixed_header = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#5B9BD5', 'font_color': '#000000',
            'border': 1,
            'text_wrap': True,   # <-- importante para que respete el salto
        })
        st_day_num = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#5B9BD5', 'border': 1
            # <- sin rotation
        })
        st_dow = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'bg_color': '#5B9BD5', 'border': 1
            # <- sin rotation
        })
        st_date = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'border': 1,
            'num_format': 'dd/mm/yyyy'
        })
        st_text_left = workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'border': 1
        })
        st_text_center = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'border': 1
        })
        st_day_cell = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'border': 1, 'text_wrap': True
        })
        st_day_cell_absent = workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'border': 1, 'text_wrap': True,
            'bg_color': '#ED7D31'  # naranja como en la imagen
        })

        # ====== Fechas dinámicas ======
        dates = list(self._iter_dates(self.date_from, self.date_to))
        start_day_col = 6

        # === columnas de días: MÁS ANCHAS (doble aprox) ===
        for i in range(len(dates)):
            ws.set_column(start_day_col + i, start_day_col + i, 10.5)

        # Fila 0: meses (merge por bloque); columnas fijas: se deja en blanco (como área del logo)
        ws.merge_range(0, 0, 0, 5, '', workbook.add_format({'border': 0}))

        # Merges por mes
        month_blocks = []
        cur_start = 0
        while cur_start < len(dates):
            m = dates[cur_start].month
            y = dates[cur_start].year
            cur_end = cur_start
            while cur_end + 1 < len(dates) and dates[cur_end + 1].month == m and dates[cur_end + 1].year == y:
                cur_end += 1
            month_blocks.append((cur_start, cur_end, m, y))
            cur_start = cur_end + 1

        for bstart, bend, m, y in month_blocks:
            c1 = start_day_col + bstart
            c2 = start_day_col + bend
            ws.merge_range(0, c1, 0, c2, self._month_name_es(m), st_month)

        # Encabezados fijos (merge vertical en filas 1-2)
        fixed_headers = [
            ('DNI', 0),
            ('APELLIDOS Y NOMBRES', 1),
            ('FECHA DE\nINGRESO', 2),     # <-- 2 filas
            ('CENTRO DE\nCOSTO', 3),      # <-- 2 filas
            ('PLANILLA', 4),
            ('OBSER', 5),
        ]
        for label, col in fixed_headers:
            ws.merge_range(1, col, 2, col, label, st_fixed_header)

        # Fila 1: día del mes / Fila 2: día semana
        for i, d in enumerate(dates):
            col = start_day_col + i
            ws.write(1, col, d.day, st_day_num)
            ws.write(2, col, self._dow_letter(d), st_dow)

        # Freeze (debajo headers y después de columnas fijas)
        ws.freeze_panes(3, start_day_col)

        # ====== Data ======
        emp_ids = self._get_employee_ids_with_attendance()
        if not emp_ids:
            return  # no hay nada que imprimir

        employees = self.env['hr.employee'].sudo().search([('id', 'in', emp_ids), ('active', '=', True)], order='name')
        employee_ids = employees.ids

        hire_map = self._get_hire_dates_map(employee_ids)
        att_map = self._get_attendance_map(employee_ids)

        data_row = 3
        for emp in employees:
            ws.set_row(data_row, 34)
            partner = emp.address_home_id if 'address_home_id' in emp._fields else False
            dni = (partner.vat or '').strip() if partner and 'vat' in partner._fields else ''
            hire_date = hire_map.get(emp.id)
            cost_center = self._get_employee_cost_center(emp)
            planilla = self._get_planilla_label(emp)

            ws.write(data_row, 0, dni, st_text_left)
            ws.write(data_row, 1, emp.name or '', st_text_left)
            if hire_date:
                ws.write(data_row, 2, hire_date, st_date)
            else:
                ws.write(data_row, 2, '', st_text_center)
            ws.write(data_row, 3, cost_center or '', st_text_center)
            ws.write(data_row, 4, planilla, st_text_center)
            ws.write(data_row, 5, '', st_text_left)  # Observaciones libre

            # Celdas por día
            for i, d in enumerate(dates):
                col = start_day_col + i
                info = att_map.get((emp.id, d))
                if not info:
                    ws.write(data_row, col, '', st_day_cell_absent)
                    continue

                tin = info.get('in')
                tout = info.get('out')

                # Formato: ingreso (línea 1) / salida (línea 2)
                parts = []
                if tin:
                    parts.append(tin.strftime('%H:%M:%S'))
                if tout:
                    parts.append(tout.strftime('%H:%M:%S'))

                cell_text = "\n".join(parts) if parts else ""
                ws.write(data_row, col, cell_text, st_day_cell if cell_text else st_day_cell_absent)

            data_row += 1
            ws.set_row(data_row, 28)

    # (ya no se usa tu _get_query anterior; si tu infraestructura lo llama, déjalo,
    #  pero este XLSX usa _get_attendance_map + empleados activos)
    def _get_query(self):
        return []
