# -*- coding: utf-8 -*-
from odoo import _, fields, models
import io as io
import base64

import logging
_logger = logging.getLogger(__name__)


class ProvinceReimbursementsReport(models.TransientModel):
    _name = 'province.reimbursements.report'
    _description = 'Reporte de reembolsos de provincia'
    _inherit = ['report.formats']

    # --------------------------
    # Helpers
    # --------------------------
    def change_state_name(self, state):
        """Reutiliza la misma traducción de estados que tu ExpensesReport."""
        final_state = ''
        if state == 'draft':
            final_state = _('Draft')
        if state == 'executive':
            final_state = _('Executive')
        if state == 'responsible':
            final_state = _('Responsible')
        if state == 'intern_control':
            final_state = _('Intern control')
        if state == 'administration':
            final_state = _('Administration')
        if state == 'to_settle':
            final_state = _('To settle')
        if state == 'settled':
            final_state = _('Settled')
        if state == 'refused':
            final_state = _('Refused')
        return final_state

    # --------------------------
    # Botón
    # --------------------------
    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')

    # --------------------------
    # Nombre de archivo
    # --------------------------
    def _get_file_name(self, function_name, file_name=False):
        return super(ProvinceReimbursementsReport, self)._get_file_name(
            function_name, file_name=_('Reporte de reembolsos de provincia')
        )

    # --------------------------
    # Hoja XLSX
    # --------------------------
    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Reporte de reembolsos de provincia'))
        ws.set_zoom(85)

        # Anchuras orientativas
        ws.set_column('B:B', 22)   # PROVINCIAS
        ws.set_column('C:C', 8)    # MES
        ws.set_column('D:D', 20)   # FECHA CREACIÓN DE RQ
        ws.set_column('E:E', 18)   # MONTO SOLICITADO
        ws.set_column('F:F', 14)   # N° RQ
        ws.set_column('G:G', 26)   # DEPOSITO A:
        ws.set_column('H:H', 26)   # CLIENTE
        ws.set_column('I:I', 16)   # N° PPTO
        ws.set_column('J:J', 12)   # C .C
        ws.set_column('K:K', 20)   # ACTIVIDAD
        ws.set_column('L:L', 36)   # DETALLE
        ws.set_column('M:M', 16)   # ESTADO
        ws.set_column('N:N', 16)   # GASTO REAL
        ws.set_column('O:O', 24)   # MONTO DE DIFERENCIA
        ws.set_column('P:P', 40)   # “de acuerdo al monto...”

        # Estilos (paleta cercana al rojo de tu imagen)
        hdr = workbook.add_format({
            'font_size': 11, 'font_color': '#FFFFFF', 'bg_color': '#B00000',
            'align': 'center', 'valign': 'vcenter', 'border': 1,
            'bold': True, 'border_color': '#FFFFFF', 'text_wrap': True,
        })
        title = workbook.add_format({
            'font_size': 16, 'bold': True, 'align': 'center', 'valign': 'vcenter',
        })
        cell = workbook.add_format({'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        cell_left = workbook.add_format({'font_size': 11, 'align': 'left', 'valign': 'vcenter', 'border': 1})
        cell_date = workbook.add_format({'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': 'dd/mm/yyyy'})
        money = workbook.add_format({'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00'})

        # Logo (opcional)
        company = self.env.user.company_id.logo
        if company:
            ws.insert_image(1, 1, 'logo.png', {
                'image_data': io.BytesIO(base64.b64decode(company)),
                'x_scale': 0.15, 'y_scale': 0.15,
            })

        # Título
        ws.merge_range('D2:I2', _('REPORTE DE REEMBOLSOS DE PROVINCIA'), title)

        # Encabezados EXACTOS
        ws.write('B5', _('PROVINCIAS'), hdr)
        ws.write('C5', _('MES'), hdr)
        ws.write('D5', _('FECHA CREACIÓN DE RQ'), hdr)
        ws.write('E5', _('MONTO SOLICITADO'), hdr)
        ws.write('F5', _('N° RQ'), hdr)
        ws.write('G5', _('DEPOSITO A:'), hdr)
        ws.write('H5', _('CLIENTE'), hdr)
        ws.write('I5', _('N° PPTO'), hdr)
        ws.write('J5', _('C .C'), hdr)
        ws.write('K5', _('ACTIVIDAD'), hdr)
        ws.write('L5', _('DETALLE'), hdr)
        ws.write('M5', _('ESTADO'), hdr)
        ws.write('N5', _('GASTO REAL'), hdr)
        ws.write('O5', _('MONTO DE DIFERENCIA (Monto Inicial - Gasto real)'), hdr)
        ws.write('P5', _('"de acuerdo al monto de diferencia" SI ES A FAVOR DE MARKETING O SUPERVISOR'), hdr)

        # Datos (agregado por RQ)
        row = 5
        for r in self._get_query_rows():
            # Diferencia y etiqueta
            monto_solicitado = float(r.get('amount') or 0.0)
            gasto_real = float(r.get('real_expense') or 0.0)
            diferencia = monto_solicitado - gasto_real
            if diferencia > 0:
                etiqueta = _('A FAVOR DE MARKETING')
            elif diferencia < 0:
                etiqueta = _('A FAVOR DE SUPERVISOR')
            else:
                etiqueta = _('SIN DIFERENCIA')

            # Provincia
            ws.write(row, 1, r.get('province') or '', cell)

            # Mes (de la fecha de creación del RQ)
            mes = r.get('rq_month')  # 1..12
            ws.write(row, 2, mes or '', cell)

            # Fecha creación RQ
            if r.get('rq_create_date'):
                ws.write_datetime(row, 3, r['rq_create_date'], cell_date)
            else:
                ws.write(row, 3, '', cell)

            # Monto solicitado
            ws.write_number(row, 4, monto_solicitado, money)

            # N° RQ
            ws.write(row, 5, r.get('requirement') or '', cell)

            # Depósito a (Girado a)
            ws.write(row, 6, r.get('paid_to') or '', cell_left)

            # Cliente (placeholder hasta confirmar campo real)
            ws.write(row, 7, r.get('client_name') or '', cell_left)

            # N° PPTO
            ws.write(row, 8, r.get('budget') or '', cell_left)

            # C .C
            ws.write(row, 9, r.get('cost_center') or '', cell)

            # Actividad (placeholder)
            ws.write(row, 10, r.get('activity_name') or '', cell_left)

            # Detalle
            ws.write(row, 11, r.get('concept') or '', cell_left)

            # Estado (del RQ)
            ws.write(row, 12, self.change_state_name(r.get('requirement_state')), cell)

            # Gasto real (total liquidado por RQ)
            ws.write_number(row, 13, gasto_real, money)

            # Diferencia y etiqueta
            ws.write_number(row, 14, diferencia, money)
            ws.write(row, 15, etiqueta, cell)

            row += 1

        # Autofiltro
        ws.autofilter(4, 1, row - 1, 15)

    # --------------------------
    # Query agregado por RQ
    # --------------------------
    def _get_query_rows(self):
        """
        Agrega por RQ:
          - rq_create_date (dr.create_date::date) y rq_month
          - province (res_province.name desde rp.province_id)
          - amount (monto solicitado del RQ: soles/u$s)
          - real_expense = SUM(s.settle_amount_sum) por RQ
          - estado del RQ
          - placeholders client_name / activity_name (vacíos)
        """
        query = """
            SELECT
                dr.id                              AS rq_id,
                dr.name                            AS requirement,
                dr.create_date::date               AS rq_create_date,
                EXTRACT(MONTH FROM dr.create_date) AS rq_month,

                -- Generales
                b.name   AS budget,
                cc.code  AS cost_center,
                rp.name  AS paid_to,
                rpr.name AS province,
                dr.concept AS concept,
                dr.requirement_state AS requirement_state,

                -- Monto solicitado (como en tu reporte original)
                CASE
                    WHEN dr.amount_soles > 0 THEN dr.amount_soles
                    WHEN dr.amount_uss   > 0 THEN dr.amount_uss
                    ELSE 0
                END AS amount,

                -- Gasto real total por RQ
                COALESCE(SUM(s.settle_amount_sum), 0) AS real_expense,

                -- Placeholders (quedarán en blanco hasta confirmar campos)
                NULL::varchar AS client_name,
                NULL::varchar AS activity_name

            FROM documental_requirements AS dr
                LEFT JOIN budget       AS b   ON b.id  = dr.budget_id
                LEFT JOIN cost_center  AS cc  ON cc.id = b.cost_center_id
                LEFT JOIN res_partner  AS rp  ON rp.id = dr.paid_to
                LEFT JOIN res_province AS rpr ON rpr.id = rp.province_id
                LEFT JOIN settlement   AS s   ON s.requirement_id = dr.id

            WHERE (dr.intern_control_signed_on IS NOT NULL OR dr.settlement_intern_control_signed_on IS NOT NULL)
              AND dr.active != FALSE
            GROUP BY
                dr.id, dr.name, dr.create_date,
                b.name, cc.code, rp.name, rpr.name,
                dr.concept, dr.requirement_state,
                dr.amount_soles, dr.amount_uss
            ORDER BY dr.name DESC
        """
        self._cr.execute(query)
        return self._cr.dictfetchall()
