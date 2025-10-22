# -*- coding: utf-8 -*-
from odoo import _, models, fields, api
from odoo.exceptions import UserError
from datetime import date

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

    # === XLSX ===
    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Attendance Report (All)'))

        ws.set_zoom(80)
        ws.set_column('A:A', 40)  # Employee
        ws.set_column('B:B', 15)  # Date
        ws.set_column('C:C', 15)  # Check-in
        ws.set_column('D:D', 15)  # Check-out
        ws.set_column('E:E', 20)  # Check-in Lat
        ws.set_column('F:F', 20)  # Check-in Lon
        ws.set_column('G:G', 20)  # Check-out Lat
        ws.set_column('H:H', 20)  # Check-out Lon
        ws.set_column('I:I', 20)  # Within Allowed Area

        header_style = {
            'font_color': '#FFFFFF',
            'bg_color': '#000000',
            'align': 'center',
            'border': 2,
            'bold': True
        }
        data_style = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'align': 'center',
            'border': 1
        }
        date_style = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'align': 'center',
            'border': 1,
            'num_format': 'dd/mm/yyyy'
        }
        time_style = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'align': 'center',
            'border': 1,
            'num_format': 'hh:mm:ss'
        }

        stl_header = workbook.add_format(header_style)
        stl_data = workbook.add_format(data_style)
        stl_date = workbook.add_format(date_style)
        stl_time = workbook.add_format(time_style)

        ws.write('A1', _('Employee'), stl_header)
        ws.write('B1', _('Date'), stl_header)
        ws.write('C1', _('Check-in'), stl_header)
        ws.write('D1', _('Check-out'), stl_header)
        ws.write('E1', _('Check-in Latitude'), stl_header)
        ws.write('F1', _('Check-in Longitude'), stl_header)
        ws.write('G1', _('Check-out Latitude'), stl_header)
        ws.write('H1', _('Check-out Longitude'), stl_header)
        ws.write('I1', _('Within Allowed Area'), stl_header)

        records = self._get_query()
        row = 1
        for r in records:
            ws.write(row, 0, r['employee'], stl_data)
            ws.write(row, 1, r['date'], stl_date)
            ws.write(row, 2, r['check_in'], stl_time)
            ws.write(row, 3, r['check_out'], stl_time)
            ws.write(row, 4, r['check_in_latitude'], stl_data)
            ws.write(row, 5, r['check_in_longitude'], stl_data)
            ws.write(row, 6, r['check_out_latitude'], stl_data)
            ws.write(row, 7, r['check_out_longitude'], stl_data)
            ws.write(row, 8, _('Yes') if r['within_allowed_area'] else _('No'), stl_data)
            row += 1

    def _get_query(self):
        """Agrupa por empleado y fecha local (America/Lima).
        - Primer check_in y último check_out del día
        - BOOL_OR de within_allowed_area
        - Solo empleados activos con asistencias en el rango
        - Filtra por fechas usando la fecha local (no UTC)
        """
        self.ensure_one()
        if not self.date_from or not self.date_to:
            return []

        tz = 'America/Lima'
        params = {
            'tz': tz,
            'date_from': self.date_from,
            'date_to': self.date_to,
        }

        query = """
            WITH attendance_data AS (
                SELECT
                    at.employee_id,
                    (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s)::date AS date_local,
                    MIN(at.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s) AS check_in_local,
                    MAX(at.check_out AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s) AS check_out_local,
                    BOOL_OR(COALESCE(at.within_allowed_area, FALSE)) AS within_allowed_area
                FROM hr_attendance at
                JOIN hr_employee he ON he.id = at.employee_id
                WHERE he.active = TRUE
                  AND (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s)::date BETWEEN %(date_from)s AND %(date_to)s
                GROUP BY at.employee_id, (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s)::date
            )
            SELECT
                he.name AS employee,
                ad.date_local AS date,
                ad.check_in_local::time AS check_in,
                ad.check_out_local::time AS check_out,
                ad.within_allowed_area,
                at_in.check_in_latitude,
                at_in.check_in_longitude,
                at_out.check_out_latitude,
                at_out.check_out_longitude
            FROM attendance_data ad
            JOIN hr_employee he ON he.id = ad.employee_id
            LEFT JOIN hr_attendance at_in 
                   ON at_in.employee_id = ad.employee_id
                  AND (at_in.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s) = ad.check_in_local
                  AND (at_in.check_in AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s)::date = ad.date_local
            LEFT JOIN hr_attendance at_out
                   ON at_out.employee_id = ad.employee_id
                  AND (at_out.check_out AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s) = ad.check_out_local
                  AND (at_out.check_out AT TIME ZONE 'UTC' AT TIME ZONE %(tz)s)::date = ad.date_local
            ORDER BY ad.date_local DESC, he.name ASC;
        """
        self._cr.execute(query, params)
        return self._cr.dictfetchall()
