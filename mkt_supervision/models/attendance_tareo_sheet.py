# -*- coding: utf-8 -*-
import calendar
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


DAY_FIELDS = [f'day_{i:02d}' for i in range(1, 32)]
ALLOWED_CODES = {'A', 'B', 'H', 'S', 'V', 'W', 'R', 'N', 'X', 'P', 'M'}

class AttendanceTareoSheet(models.Model):
    _name = 'attendance.tareo.sheet'
    _description = 'Tareo mensual editable'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Descripción', compute='_compute_name', store=True)
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        default=lambda self: self.env.company,
        required=True,
    )
    responsible_id = fields.Many2one(
        'res.users',
        string='Responsable',
        default=lambda self: self.env.user,
    )

    month = fields.Selection(
        [(str(i), str(i)) for i in range(1, 13)],
        string='Mes',
        required=True,
    )
    year = fields.Char(
        string='Año',
        required=True,
    )

    date_from = fields.Date(string='Desde')
    date_to = fields.Date(string='Hasta')

    days_in_month = fields.Integer(
        string='Días del mes',
        compute='_compute_days_in_month',
        store=True,
    )

    general_comments = fields.Text(
        string='Comentarios generales',
        help='Comentarios u observaciones generales del tareo del mes.',
        tracking=True,
    )

    line_ids = fields.One2many(
        'attendance.tareo.line',
        'sheet_id',
        string='Líneas de tareo',
    )

    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('sent', 'Enviado'),
            ('approved', 'Aceptado'),
            ('rejected', 'Rechazado'),
        ],
        string='Estado',
        default='draft',
        tracking=True,
    )

    @api.depends('month', 'year')
    def _compute_days_in_month(self):
        for rec in self:
            if rec.month and rec.year:
                try:
                    month_int = int(rec.month)
                    year_int = int(rec.year)
                    rec.days_in_month = calendar.monthrange(year_int, month_int)[1]
                except Exception:
                    rec.days_in_month = 0
            else:
                rec.days_in_month = 0

    def action_send(self):
        """Enviar el tareo para aprobación."""
        for sheet in self:
            if not sheet.line_ids:
                raise ValidationError(_('No hay líneas de tareo para enviar.'))
            sheet.state = 'sent'
            sheet.message_post(body=_('Tareo enviado para aprobación.'))

    def action_reset_to_draft(self):
        """Restablecer el tareo a borrador (solo desde sent)."""
        for sheet in self:
            if sheet.state != 'sent':
                raise ValidationError(_('Solo se pueden restablecer a borrador los tareos enviados.'))
            sheet.state = 'draft'
            sheet.message_post(body=_('Tareo restablecido a borrador.'))

    def action_approve(self):
        """Aceptar el tareo (solo HR Contract Manager)."""
        for sheet in self:
            sheet.state = 'approved'
            sheet.message_post(body=_('Tareo aceptado.'))

    def action_reject(self):
        """Rechazar el tareo (solo HR Contract Manager)."""
        for sheet in self:
            sheet.state = 'rejected'
            sheet.message_post(body=_('Tareo rechazado. Puede ser editado y reenviado.'))

    def unlink(self):
        """No permite eliminar registros en estado sent o approved."""
        for sheet in self:
            if sheet.state in ('sent', 'approved'):
                raise ValidationError(
                    _('No se puede eliminar un tareo que ha sido enviado o aprobado. '
                      'Estado actual: %s') % dict(sheet._fields['state'].selection).get(sheet.state)
                )
        return super(AttendanceTareoSheet, self).unlink()

    @api.depends('month', 'year')
    def _compute_name(self):
        for rec in self:
            if rec.month and rec.year:
                rec.name = _('Tareo %s-%s') % (rec.month, rec.year)
            else:
                rec.name = _('Tareo')


class AttendanceTareoLine(models.Model):
    _name = 'attendance.tareo.line'
    _description = 'Línea de tareo mensual'

    sheet_id = fields.Many2one(
        'attendance.tareo.sheet',
        string='Hoja de tareo',
        required=True,
        ondelete='cascade',
    )
    sheet_days_in_month = fields.Integer(
        related='sheet_id.days_in_month',
        string='Días del mes',
        store=False,
    )
    employee_id = fields.Many2one(
        'hr.employee',
        string='Empleado',
        required=True,
        domain="[('id', 'in', available_employee_ids)]",
    )
    available_employee_ids = fields.Many2many(
        'hr.employee',
        compute='_compute_available_employees',
        string='Empleados disponibles',
    )
    dni = fields.Char(string='DNI', compute='_compute_employee_data', store=True)
    employee_name = fields.Char(string='Nombre', compute='_compute_employee_data', store=True)

    # 31 días (el mes decidirá cuáles se usan realmente)
    day_01 = fields.Char(string='01', size=2)
    day_02 = fields.Char(string='02', size=2)
    day_03 = fields.Char(string='03', size=2)
    day_04 = fields.Char(string='04', size=2)
    day_05 = fields.Char(string='05', size=2)
    day_06 = fields.Char(string='06', size=2)
    day_07 = fields.Char(string='07', size=2)
    day_08 = fields.Char(string='08', size=2)
    day_09 = fields.Char(string='09', size=2)
    day_10 = fields.Char(string='10', size=2)
    day_11 = fields.Char(string='11', size=2)
    day_12 = fields.Char(string='12', size=2)
    day_13 = fields.Char(string='13', size=2)
    day_14 = fields.Char(string='14', size=2)
    day_15 = fields.Char(string='15', size=2)
    day_16 = fields.Char(string='16', size=2)
    day_17 = fields.Char(string='17', size=2)
    day_18 = fields.Char(string='18', size=2)
    day_19 = fields.Char(string='19', size=2)
    day_20 = fields.Char(string='20', size=2)
    day_21 = fields.Char(string='21', size=2)
    day_22 = fields.Char(string='22', size=2)
    day_23 = fields.Char(string='23', size=2)
    day_24 = fields.Char(string='24', size=2)
    day_25 = fields.Char(string='25', size=2)
    day_26 = fields.Char(string='26', size=2)
    day_27 = fields.Char(string='27', size=2)
    day_28 = fields.Char(string='28', size=2)
    day_29 = fields.Char(string='29', size=2)
    day_30 = fields.Char(string='30', size=2)
    day_31 = fields.Char(string='31', size=2)

    # Totales verticales (mapean a tus 9 columnas)
    days_worked = fields.Integer(
        string='Días trabajados',
        compute='_compute_totals',
        store=True,
    )
    days_vacaciones = fields.Integer(
        string='Días vacaciones',
        compute='_compute_totals',
        store=True,
    )
    days_subsidio_maternidad = fields.Integer(
        string='Subsidio maternidad',
        compute='_compute_totals',
        store=True,
    )
    days_licencia_paternidad = fields.Integer(
        string='Licencia paternidad',
        compute='_compute_totals',
        store=True,
    )
    days_dm_menor_20 = fields.Integer(
        string='Descanso médico <20 días',
        compute='_compute_totals',
        store=True,
    )
    days_dm_mayor_20 = fields.Integer(
        string='Descanso médico ≥20 días',
        compute='_compute_totals',
        store=True,
    )
    days_feriados = fields.Integer(
        string='Feriados',
        compute='_compute_totals',
        store=True,
    )
    days_no_laborados = fields.Integer(
        string='Días no laborados',
        compute='_compute_totals',
        store=True,
    )
    days_lic_sin_goce = fields.Integer(
        string='Licencia sin goce',
        compute='_compute_totals',
        store=True,
    )
    
    # Nuevos campos
    days_inasistencias = fields.Integer(
        string='Inasistencias',
        compute='_compute_totals',
        store=True,
        help='Suma de Faltas (B) + Licencias sin goce (X)'
    )
    total_days = fields.Integer(
        string='Total días',
        compute='_compute_totals',
        store=True,
        help='Autosuma de todos los conceptos'
    )
    attendance_percentage = fields.Float(
        string='% Asistencia',
        compute='_compute_totals',
        store=True,
        help='Porcentaje de asistencias sobre total de días del mes'
    )
    days_difference = fields.Integer(
        string='Diferencia',
        compute='_compute_totals',
        store=True,
        help='Diferencia entre días del mes y total contabilizado'
    )
    comments = fields.Text(
        string='Comentarios',
        help='Observaciones sobre el tratamiento del mes'
    )
    
    # Campo relacionado para controlar edición en vista
    sheet_state = fields.Selection(
        related='sheet_id.state',
        string='Estado de la hoja',
        readonly=True,
        store=False,
    )

    @api.depends('sheet_id', 'sheet_id.line_ids', 'sheet_id.line_ids.employee_id')
    def _compute_available_employees(self):
        """
        Calcula los empleados disponibles para agregar:
        - El usuario actual
        - Todos sus subordinados recursivamente
        - Excluyendo los que ya están en otras líneas de este tareo
        """
        for rec in self:
            if not rec.sheet_id:
                rec.available_employee_ids = False
                continue
            
            # Obtener el empleado del usuario actual
            my_employee = self.env['hr.employee'].search([
                ('user_id', '=', self.env.uid)
            ], limit=1)
            
            if not my_employee:
                rec.available_employee_ids = False
                continue
            
            # Incluir al empleado actual
            all_employees = my_employee
            to_check = my_employee
            
            # Buscar recursivamente todos los subordinados
            while to_check:
                children = self.env['hr.employee'].search([
                    ('parent_id', 'in', to_check.ids)
                ])
                to_check = children - all_employees
                all_employees |= to_check
            
            # Excluir empleados que ya están en otras líneas de este tareo
            existing_employees = rec.sheet_id.line_ids.filtered(
                lambda l: l.id != rec.id
            ).mapped('employee_id')
            
            available = all_employees - existing_employees
            rec.available_employee_ids = available

    @api.depends('employee_id')
    def _compute_employee_data(self):
        """Calcula DNI y nombre del empleado al seleccionarlo."""
        for rec in self:
            if rec.employee_id:
                partner = rec.employee_id.user_id.partner_id
                rec.dni = partner.vat or ''
                rec.employee_name = partner.name or rec.employee_id.name or ''
            else:
                rec.dni = ''
                rec.employee_name = ''

    @api.model
    def create(self, vals):
        """
        Al crear una línea nueva, generamos automáticamente el tareo
        basado en asistencias y ausencias del mes.
        """
        line = super(AttendanceTareoLine, self).create(vals)
        
        # Si no se proporcionaron datos de días, los generamos
        if line.sheet_id and line.employee_id:
            # Verificar si no se proporcionaron datos de días
            has_day_data = any(vals.get(f'day_{i:02d}') for i in range(1, 32))
            
            if not has_day_data:
                line._generate_tareo_data()
        
        return line

    def _generate_tareo_data(self):
        """
        Genera los datos del tareo para este empleado basado en
        asistencias y ausencias del mes de la hoja.
        """
        self.ensure_one()
        
        if not self.sheet_id or not self.employee_id:
            return
        
        sheet = self.sheet_id
        mes = int(sheet.month)
        anio = int(sheet.year)
        first_day = datetime(anio, mes, 1).date()
        num_days = calendar.monthrange(anio, mes)[1]
        last_day = datetime(anio, mes, num_days).date()
        
        emp_id = self.employee_id.id
        
        # Obtener asistencias
        self.env.cr.execute("""
            SELECT DISTINCT (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS fecha
            FROM hr_attendance at
            WHERE (at.check_in AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date BETWEEN %s AND %s
              AND at.check_in IS NOT NULL
              AND at.employee_id = %s
        """, (first_day, last_day, emp_id))
        attend_dates = set(row[0] for row in self.env.cr.fetchall())
        
        # Obtener licencias
        self.env.cr.execute("""
            SELECT (hl.date_from AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS inicio,
                   (hl.date_to   AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS fin,
                   hlt.sigla AS sigla
            FROM hr_leave hl
            JOIN hr_leave_type hlt ON hlt.id = hl.holiday_status_id
            WHERE hl.state = 'validate'
              AND (hl.date_from AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date <= %s
              AND (hl.date_to   AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date >= %s
              AND hl.employee_id = %s
        """, (last_day, first_day, emp_id))
        
        leaves_map = {}
        for rec in self.env.cr.dictfetchall():
            ini = rec['inicio']
            fin = rec['fin']
            sig = rec['sigla'] or ''
            current = max(ini, first_day)
            end_range = min(fin, last_day)
            for d in range((end_range - current).days + 1):
                dia = current + timedelta(days=d)
                leaves_map[dia] = sig
        
        holiday_dates = self._get_holiday_dates_set()

        vals = {}
        for day in range(1, num_days + 1):
            fecha = datetime(anio, mes, day).date()
            field_name = f'day_{day:02d}'

            # FERIADO registrado => H (prioridad máxima)
            if fecha in holiday_dates:
                vals[field_name] = 'H'
            elif fecha.weekday() in (5, 6):
                vals[field_name] = 'H'
            elif fecha in leaves_map:
                vals[field_name] = leaves_map[fecha]
            elif fecha in attend_dates:
                vals[field_name] = 'A'
            else:
                vals[field_name] = ''
                vals[field_name] = ''
        
        self.write(vals)

    @api.depends(
        'day_01', 'day_02', 'day_03', 'day_04', 'day_05', 'day_06', 'day_07',
        'day_08', 'day_09', 'day_10', 'day_11', 'day_12', 'day_13', 'day_14',
        'day_15', 'day_16', 'day_17', 'day_18', 'day_19', 'day_20', 'day_21',
        'day_22', 'day_23', 'day_24', 'day_25', 'day_26', 'day_27', 'day_28',
        'day_29', 'day_30', 'day_31',
        'sheet_id.month', 'sheet_id.year',
    )
    def _compute_totals(self):
        """
        Mapeo de códigos según leyenda:

        A = Attendance (asistencia)                -> días trabajados
        B = aBsence (falta)                        -> inasistencia
        H = Holidays (descanso semanal/feriado)    -> día trabajado
        S = Sick Leave (1-20 días)                 -> DM < 20
        V = Vacation                               -> vacaciones
        W = Holiday Working (trabaja en feriado)   -> trabajado + feriado
        R = medical Rest (subsidio/ESSALUD)        -> DM >= 20
        N = No vínculo laboral                     -> no laborado
        X = Licencia sin goce de haber             -> lic. sin goce + inasistencia
        P = Paternity leave                        -> licencia paternidad
        M = Maternity leave                        -> subsidio maternidad
        F = Feriado no trabajado (opcional)        -> feriados
        NL = No laborado (código libre adicional)  -> no laborado
        """
        for rec in self:
            dias_trabajados = 0
            vacaciones = 0
            subsidio_maternidad = 0
            lic_paternidad = 0
            dm_menor = 0
            dm_mayor = 0
            feriados = 0
            no_laborados = 0
            lic_sin_goce = 0
            faltas = 0
            no_vinculo = 0

            # Contar por código
            for i in range(1, 32):
                val = (getattr(rec, f'day_{i:02d}') or '').upper().strip()
                if not val:
                    continue

                if val == 'A':
                    dias_trabajados += 1

                elif val == 'H':
                    # Descanso semanal / feriado NO trabajado pero se considera día laborado
                    dias_trabajados += 1

                elif val == 'W':
                    # Trabajo en feriado: cuenta como trabajado y como feriado
                    dias_trabajados += 1
                    feriados += 1

                elif val == 'V':
                    vacaciones += 1

                elif val == 'S':
                    # Enfermedad justificada (1ros 20 días)
                    dm_menor += 1

                elif val == 'R':
                    # Descanso médico (subsidio)
                    dm_mayor += 1

                elif val == 'M':
                    # Licencia por maternidad
                    subsidio_maternidad += 1

                elif val == 'P':
                    # Licencia por paternidad
                    lic_paternidad += 1

                elif val == 'X':
                    # Licencia sin goce de haber (cuenta como inasistencia)
                    lic_sin_goce += 1

                elif val == 'B':
                    # Falta
                    faltas += 1

                elif val == 'N':
                    # No vínculo laboral
                    no_vinculo += 1

                else:
                    # Cualquier código desconocido lo puedes considerar no laborado
                    no_laborados += 1

            # Totales básicos
            rec.days_worked = dias_trabajados
            rec.days_vacaciones = vacaciones
            rec.days_subsidio_maternidad = subsidio_maternidad
            rec.days_licencia_paternidad = lic_paternidad
            rec.days_dm_menor_20 = dm_menor
            rec.days_dm_mayor_20 = dm_mayor
            rec.days_feriados = feriados
            rec.days_no_laborados = no_laborados + no_vinculo
            rec.days_lic_sin_goce = lic_sin_goce

            # Inasistencias = B + X
            rec.days_inasistencias = faltas + lic_sin_goce

            # Autosuma de todos los conceptos (incluyendo faltas y lic. sin goce)
            total_days = (
                dias_trabajados
                + vacaciones
                + subsidio_maternidad
                + lic_paternidad
                + dm_menor
                + dm_mayor
                + feriados
                + no_laborados
                + no_vinculo
                + lic_sin_goce
                + faltas
            )
            rec.total_days = total_days

            # Días del mes (para % y diferencia)
            days_in_month = 0
            try:
                if rec.sheet_id and rec.sheet_id.month and rec.sheet_id.year:
                    month_int = int(rec.sheet_id.month)
                    year_int = int(rec.sheet_id.year)
                    days_in_month = calendar.monthrange(year_int, month_int)[1]
            except Exception:
                days_in_month = 0

            # Diferencia entre calendario y lo contabilizado
            if days_in_month:
                rec.days_difference = days_in_month - total_days
                # Ojo: widget="percentage" ya multiplica por 100,
                # así que aquí guardamos solo la fracción 0..1
                rec.attendance_percentage = dias_trabajados / float(days_in_month)
            else:
                rec.days_difference = 0
                rec.attendance_percentage = 0.0

    def _get_holiday_dates_set(self):
        self.ensure_one()
        sheet = self.sheet_id
        if not (sheet and sheet.company_id and sheet.year and sheet.month):
            return set()

        year_int = int(sheet.year)
        month_int = int(sheet.month)
        first_day = datetime(year_int, month_int, 1).date()
        last_day = datetime(year_int, month_int, sheet.days_in_month or calendar.monthrange(year_int, month_int)[1]).date()

        lines = self.env['attendance.tareo.holiday.line'].search([
            ('company_id', '=', sheet.company_id.id),
            ('year', '=', year_int),
            ('active', '=', True),
            ('year_id.active', '=', True),
            ('date', '>=', first_day),
            ('date', '<=', last_day),
        ])
        return set(lines.mapped('date'))

    @api.constrains(*DAY_FIELDS, 'sheet_id', 'sheet_id.days_in_month')
    def _check_day_codes(self):
        for rec in self:
            dim = rec.sheet_days_in_month or 0
            holidays = rec._get_holiday_dates_set()
            holiday_days = {d.day for d in holidays}

            for i in range(1, 32):
                field_name = f'day_{i:02d}'
                val = (getattr(rec, field_name) or '').strip().upper()

                if dim and i > dim and val:
                    raise ValidationError(_("No puedes llenar el día %02d porque el mes tiene %s días.") % (i, dim))

                if val and val not in ALLOWED_CODES:
                    raise ValidationError(_("Código inválido '%s' en el día %02d.\nPermitidos: %s") %
                                        (val, i, ', '.join(sorted(ALLOWED_CODES))))

                if i in holiday_days and val != 'H':
                    raise ValidationError(_("El día %02d es feriado y debe ser 'H'.") % i)


    def _normalize_day_vals(self, vals):
        for f in DAY_FIELDS:
            if f in vals and vals[f]:
                vals[f] = (vals[f] or '').strip().upper()
        return vals
    
    def _sanitize_out_of_range_vals(self, vals, days_in_month):
        """Fuerza a vacío los días > days_in_month (para evitar data inválida histórica)."""
        if not days_in_month:
            return vals
        vals2 = dict(vals)
        for i in range(days_in_month + 1, 32):
            k = f'day_{i:02d}'
            # si el usuario intenta poner algo en un día que no existe, error
            if k in vals2 and vals2[k]:
                raise ValidationError(_("No puedes llenar el día %02d porque el mes tiene %s días.") % (i, days_in_month))
            # y si no lo toca, igual lo limpiamos
            vals2.setdefault(k, False)
        return vals2

    @api.model
    def create(self, vals):
        vals = self._normalize_day_vals(vals)
        line = super().create(vals)

        # genera tareo si corresponde
        if line.sheet_id and line.employee_id:
            has_day_data = any(vals.get(f'day_{i:02d}') for i in range(1, 32))
            if not has_day_data:
                line._generate_tareo_data()

        # sanea días fuera de rango (por si quedaron)
        dim = line.sheet_id.days_in_month or 0
        if dim:
            clean = {f'day_{i:02d}': False for i in range(dim + 1, 32)}
            if clean:
                super(AttendanceTareoLine, line).write(clean)
        return line

    def write(self, vals):
        vals = self._normalize_day_vals(vals)

        # Importante: write masivo (feriados) => agrupar por hoja (días del mes)
        by_dim = {}
        for rec in self:
            dim = rec.sheet_id.days_in_month or 0
            by_dim.setdefault(dim, self.env['attendance.tareo.line'])
            by_dim[dim] |= rec

        for dim, recs in by_dim.items():
            vals2 = self._sanitize_out_of_range_vals(vals, dim) if dim else vals
            super(AttendanceTareoLine, recs).write(vals2)

        return True
    

class AttendanceTareoHolidayYear(models.Model):
    _name = 'attendance.tareo.holiday.year'
    _description = 'Feriados por año (Tareo)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, id desc'

    name = fields.Char(string='Descripción', compute='_compute_name', store=True)
    year = fields.Integer(string='Año', required=True, tracking=True)
    company_id = fields.Many2one(
        'res.company', string='Compañía', required=True,
        default=lambda self: self.env.company, tracking=True
    )
    active = fields.Boolean(default=True)

    line_ids = fields.One2many(
        'attendance.tareo.holiday.line', 'year_id',
        string='Fechas feriado', copy=True
    )

    _sql_constraints = [
        ('holiday_year_company_uniq', 'unique(company_id, year)',
         'Ya existe un registro de feriados para ese año y compañía.'),
    ]

    @api.depends('year')
    def _compute_name(self):
        for r in self:
            r.name = _('Feriados %s') % (r.year or '')


class AttendanceTareoHolidayLine(models.Model):
    _name = 'attendance.tareo.holiday.line'
    _description = 'Fecha feriado (Tareo)'
    _order = 'date asc, id asc'

    year_id = fields.Many2one(
        'attendance.tareo.holiday.year',
        string='Feriados del año', required=True, ondelete='cascade', index=True
    )
    company_id = fields.Many2one(
        related='year_id.company_id', string='Compañía', store=True, readonly=True
    )
    year = fields.Integer(related='year_id.year', store=True, readonly=True)

    date = fields.Date(string='Fecha', required=True, index=True)
    description = fields.Char(string='Descripción')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('holiday_line_uniq', 'unique(year_id, date)',
         'Esa fecha ya existe dentro del registro de feriados del año.'),
    ]

    @api.constrains('date', 'year_id')
    def _check_date_matches_year(self):
        for r in self:
            if r.date and r.year_id and r.year_id.year and r.date.year != r.year_id.year:
                raise ValidationError(_("La fecha %s no corresponde al año %s.") % (r.date, r.year_id.year))

    # ---------- Aplicación a tareos ya creados ----------
    def _apply_date_to_existing_sheets(self, d, set_h=True):
        """Marca 'H' (o limpia) en todos los tareos del mes/año de esa fecha."""
        Sheet = self.env['attendance.tareo.sheet'].sudo()
        Line = self.env['attendance.tareo.line'].sudo()

        sheets = Sheet.search([
            ('company_id', '=', self.company_id.id),
            ('month', '=', str(d.month)),
            ('year', '=', str(d.year)),
            ('state', '!=', 'approved'),
        ])
        if not sheets:
            return

        field_name = f'day_{d.day:02d}'

        if set_h:
            # Poner H a todos (bloqueado por constraint)
            Line.search([('sheet_id', 'in', sheets.ids)]).write({field_name: 'H'})
        else:
            # Limpiar solo si NO es fin de semana y solo si estaba en H
            # (evita borrar un H de sábado/domingo)
            if d.weekday() in (5, 6):
                return
            lines = Line.search([('sheet_id', 'in', sheets.ids)])
            to_clear = lines.filtered(lambda l: (getattr(l, field_name) or '').strip().upper() == 'H')
            if to_clear:
                to_clear.write({field_name: ''})

    @api.model
    def create(self, vals):
        rec = super().create(vals)
        if rec.active and rec.year_id.active and rec.date:
            rec._apply_date_to_existing_sheets(rec.date, set_h=True)
        return rec

    def write(self, vals):
        old = {r.id: (r.date, r.active, r.year_id.active) for r in self}
        res = super().write(vals)

        for r in self:
            old_date, old_active, old_year_active = old.get(r.id, (None, None, None))
            new_date = r.date
            new_active = r.active and r.year_id.active

            # si antes aplicaba y ahora no => limpiar
            if old_date and (old_active and old_year_active) and (not new_active or (new_date and new_date != old_date)):
                r._apply_date_to_existing_sheets(old_date, set_h=False)

            # si ahora aplica => aplicar
            if new_date and new_active and (new_date != old_date or not (old_active and old_year_active)):
                r._apply_date_to_existing_sheets(new_date, set_h=True)

        return res

    def unlink(self):
        for r in self:
            if r.active and r.year_id.active and r.date:
                r._apply_date_to_existing_sheets(r.date, set_h=False)
        return super().unlink()