# -*- coding: utf-8 -*-
from odoo import _, models
import io as io
import base64

import logging
_logger = logging.getLogger(__name__)


class ProvinceReport(models.TransientModel):
    _name = 'province.report'
    _description = 'Province Report'
    _inherit = ['report.formats']  # mismo mixin que tu reporte base

    # === Acción principal ===
    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')

    # === Nombre de archivo ===
    def _get_file_name(self, function_name, file_name=False):
        return super(ProvinceReport, self)._get_file_name(
            function_name, file_name=_('Expenses report (simple)'),
        )

    # === Generación de hoja XLSX ===
    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Expenses report (simple)'))
        ws.set_zoom(90)

        # --- Anchos (zona general) ---
        ws.set_column('B:B', 14)   # Fecha creación RQ
        ws.set_column('C:C', 18)   # Ciudad (Province)
        ws.set_column('D:D', 28)   # Girado a (Paid to)
        ws.set_column('E:E', 18)   # Monto del requerimiento
        ws.set_column('F:F', 12)   # RQ N°
        ws.set_column('G:G', 20)   # Presupuesto
        ws.set_column('H:H', 12)   # CC
        ws.set_column('I:I', 36)   # Detalle/Concepto

        # --- Anchos (detalle de gastos) ---
        ws.set_column('J:J', 18)   # Monto real de gasto
        ws.set_column('K:K', 20)   # Documento (tipo)
        ws.set_column('L:L', 16)   # Fecha emisión
        ws.set_column('M:M', 20)   # N° documento
        ws.set_column('N:N', 16)   # Total sin IGV
        ws.set_column('O:O', 16)   # Total

        # === Estilos (paleta y formatos) ===
        hdr = workbook.add_format({
            'font_size': 11, 'font_color': '#FFFFFF', 'bg_color': '#FF3103',
            'align': 'center', 'valign': 'vcenter', 'border': 1, 'bold': True,
            'border_color': '#FFFFFF', 'text_wrap': True,
        })
        title = workbook.add_format({
            'font_size': 16, 'bold': True, 'align': 'center', 'valign': 'vcenter',
        })
        cell = workbook.add_format({'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1})
        cell_left = workbook.add_format({'font_size': 11, 'align': 'left', 'valign': 'vcenter', 'border': 1})
        cell_date = workbook.add_format({'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': 'dd/mm/yyyy'})
        cell_amt = workbook.add_format({'font_size': 11, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'num_format': '#,##0.00'})

        # Logo (opcional)
        company = self.env.user.company_id.logo
        if company:
            ws.insert_image(1, 1, 'logo.png', {
                'image_data': io.BytesIO(base64.b64decode(company)),
                'x_scale': 0.15, 'y_scale': 0.15,
            })

        # Título
        ws.merge_range('D2:I2', _('EXPENSES REPORT (SIMPLE)'), title)

        # === Encabezados ===
        # Información general
        ws.write('B5', _('RQ CREATION DATE'), hdr)          # 1) fecha creación RQ
        ws.write('C5', _('CITY (PROVINCE)'), hdr)           # 2) ciudad (province)
        ws.write('D5', _('PAID TO'), hdr)
        ws.write('E5', _('REQUIREMENT AMOUNT'), hdr)        # 3) monto del requerimiento
        ws.write('F5', _('RQ N°'), hdr)
        ws.write('G5', _('BUDGET'), hdr)                    # 4) presupuesto
        ws.write('H5', _('CC'), hdr)                        # 5) CC
        ws.write('I5', _('DETAIL / CONCEPT'), hdr)

        # Detalle de gastos
        ws.write('J5', _('REAL EXPENSE AMOUNT'), hdr)
        ws.write('K5', _('DOCUMENT (INVOICE/RH, ETC)'), hdr)
        ws.write('L5', _('ISSUE DATE'), hdr)
        ws.write('M5', _('DOCUMENT N°'), hdr)
        ws.write('N5', _('TOTAL W/O IGV'), hdr)
        ws.write('O5', _('TOTAL'), hdr)

        # === Datos ===
        row = 5
        for rec in self._get_query_simple():
            # Fecha creación RQ
            if rec.get('rq_create_date'):
                ws.write_datetime(row, 1, rec['rq_create_date'], cell_date)
            else:
                ws.write(row, 1, '', cell)

            # Ciudad (Province)
            ws.write(row, 2, rec.get('province') or '', cell)

            # Paid to
            ws.write(row, 3, rec.get('paid_to') or '', cell_left)

            # Monto del requerimiento
            ws.write_number(row, 4, float(rec.get('amount') or 0.0), cell_amt)

            # RQ N°
            ws.write(row, 5, rec.get('requirement') or '', cell)

            # Presupuesto / CC
            ws.write(row, 6, rec.get('budget') or '', cell_left)
            ws.write(row, 7, rec.get('cost_center') or '', cell)

            # Detalle / Concepto
            ws.write(row, 8, rec.get('concept') or '', cell_left)

            # --- Detalle de gastos ---
            ws.write_number(row, 9, float(rec.get('settle_amount') or 0.0), cell_amt)  # Monto real de gasto
            ws.write(row, 10, rec.get('document_type') or '', cell)
            if rec.get('settle_date'):
                ws.write_datetime(row, 11, rec['settle_date'], cell_date)
            else:
                ws.write(row, 11, '', cell)
            ws.write(row, 12, rec.get('movement_document') or '', cell)
            ws.write_number(row, 13, float(rec.get('amount_line') or 0.0), cell_amt)   # Total sin IGV
            ws.write_number(row, 14, float(rec.get('settle_amount') or 0.0), cell_amt) # Total

            row += 1

        # Auto-filtro sobre todo el rango con datos
        ws.autofilter(4, 1, row - 1, 14)

    # === Query recortada e integrada con tus 5 campos solicitados ===
    def _get_query_simple(self):
        """
        Campos clave:
          - rq_create_date: dr.create_date::date
          - province: rpr.name
          - amount (monto del requerimiento): amount_soles / amount_uss
          - budget: b.name
          - cost_center: cc.code
        Más: paid_to, requirement, concept, y detalle de gastos (settle_*).
        """
        query = """
            SELECT
                -- Nueva: fecha de creación RQ (solo date)
                dr.create_date::date AS rq_create_date,

                -- Generales
                b.name AS budget,
                cc.code AS cost_center,
                rp.name AS paid_to,
                rpr.name AS province,
                dr.concept AS concept,
                dr.name AS requirement,
                dr.amount_currency_type AS currency,
                CASE
                    WHEN dr.amount_soles > 0 THEN dr.amount_soles
                    WHEN dr.amount_uss   > 0 THEN dr.amount_uss
                    ELSE 0
                END AS amount,

                -- Detalle de gastos
                s.date AS settle_date,
                slp.name AS document_type,
                COALESCE(s.movement_number, s.document) AS movement_document,
                s.settle_amount_sum AS settle_amount,
                CAST((s.settle_amount_sum - s.settle_igv_sum) AS numeric(10,2)) AS amount_line

            FROM documental_requirements AS dr
                LEFT JOIN budget               AS b   ON b.id  = dr.budget_id
                LEFT JOIN cost_center          AS cc  ON cc.id = b.cost_center_id
                LEFT JOIN res_partner          AS rp  ON rp.id = dr.paid_to
                LEFT JOIN res_province         AS rpr ON rpr.id = rp.province_id
                LEFT JOIN settlement           AS s   ON s.requirement_id = dr.id
                LEFT JOIN settlement_line_type AS slp ON slp.id = s.document_type_id

            WHERE (dr.intern_control_signed_on IS NOT NULL OR dr.settlement_intern_control_signed_on IS NOT NULL)
              AND dr.active != FALSE
            ORDER BY dr.name DESC, s.date ASC
        """
        self._cr.execute(query)
        return self._cr.dictfetchall()
