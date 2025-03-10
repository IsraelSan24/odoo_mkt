from odoo import models, _


class MobilityReport(models.TransientModel):
    _name = 'mobility.report'
    _description = 'Mobility Report XLSX'
    _inherit = ['report.formats']


    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')


    def _get_file_name(self, function_name, file_name=False):
        dic_name = super(MobilityReport, self)._get_file_name(function_name, file_name=_('Mobility Report'))
        return dic_name
    
    
    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Mobility Report'))

        ws.set_zoom(70)
        ws.set_column('A:A', 16)  # mdate (Fecha de movilidad)
        ws.set_column('B:B', 25)  # name (Nombre)
        ws.set_column('C:C', 20)  # requirement (Requisito)
        ws.set_column('D:D', 20)  # budget (Presupuesto)
        ws.set_column('E:E', 10)  # cost_center (Centro de costo)
        ws.set_column('F:F', 15)  # dni (Documento de identidad)
        ws.set_column('G:G', 45)  # full_name (Nombre completo)
        ws.set_column('H:H', 18)  # amount_total (Monto total)
        ws.set_column('I:I', 15)  # amount (Monto)
        ws.set_column('J:J', 24)  # cumulative_sum (Suma acumulada)
        ws.set_column('K:K', 30)  # reason (Motivo)
        ws.set_column('L:L', 25)  # origin_place (Lugar de origen)
        ws.set_column('M:M', 25)  # destiny (Destino)
        ws.set_column('N:N', 16)  # ldate (Fecha de línea)

        style_header = workbook.add_format({
            'font_color': '#FFFFFF', 'bg_color': '#000000', 'align': 'center', 'border': 2, 'bold': True
        })
        style_data = workbook.add_format({
            'font_color': '#000000', 'bg_color': '#FFFFFF', 'align': 'center', 'border': 1
        })
        style_date = workbook.add_format({
            'font_color': '#000000', 'bg_color': '#FFFFFF', 'align': 'center', 'border': 1, 'num_format': 'dd/mm/yyyy'
        })
        style_amount = workbook.add_format({
            'font_color': '#000000', 'bg_color': '#FFFFFF', 'align': 'right', 'border': 1, 'num_format': '#,##0.00'
        })
        style_date_highlight = workbook.add_format({
            'font_color': '#000000', 'bg_color': '#A9A9A9', 'align': 'center', 'border': 1, 'num_format': 'dd/mm/yyyy'
        })
        style_amount_highlight = workbook.add_format({
            'font_color': '#000000', 'bg_color': '#A9A9A9', 'align': 'right', 'border': 1, 'num_format': '#,##0.00'
        })
        style_data_highlight = workbook.add_format({
            'font_color': '#000000', 'bg_color': '#A9A9A9', 'align': 'center', 'border': 1
        })

        headers = [
            _('Mobility Date'), _('Mobility Name'), _('Requirement'), _('Budget'), _('CC'),
            _('DNI'), _('Full Name'), _('Amount Total'), _('Amount'), _('Cumulative Amount'),
            _('Reason'), _('From'), _('To'), _('Line Date')
        ]
        for col, header in enumerate(headers):
            ws.write(0, col, header, style_header)

        records_data = self._get_query()
        row = 1
        last_mobility_id = None

        for line in records_data:
            current_mobility_id = line.get('documental_mobility_id')
            is_first_row = current_mobility_id != last_mobility_id
            style1 = style_data_highlight if is_first_row else style_data
            style2 = style_amount_highlight if is_first_row else style_amount
            style3 = style_date_highlight if is_first_row else style_date

            ws.write(row, 0, line['mdate'], style3)
            ws.write(row, 1, line['name'], style1)
            ws.write(row, 2, line['requirement'], style1)
            ws.write(row, 3, line['budget'], style1)
            ws.write(row, 4, line['cost_center'], style1)
            ws.write(row, 5, line['dni'], style1)
            ws.write(row, 6, line['full_name'] if is_first_row else '', style1)
            ws.write(row, 7, line['amount_total'] if is_first_row else '', style2)
            ws.write(row, 8, line['amount'], style2)
            ws.write(row, 9, line['cumulative_sum'], style2)
            ws.write(row, 10, line['reason'], style1)
            ws.write(row, 11, line['origin_place'], style1)
            ws.write(row, 12, line['destiny'], style1)
            ws.write(row, 13, line['ldate'], style3)

            last_mobility_id = current_mobility_id
            row += 1


    def _get_query(self):
        query = """
            SELECT
                dme.id AS documental_mobility_id,
                (dme.date AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS mdate,
                (dmed.date AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima')::date AS ldate,
                b.name AS budget,
                cc.code AS cost_center,
                dme.dni AS dni,
                dmed.amount AS amount,
                SUM(dmed.amount) OVER(PARTITION BY dme.dni, dmed.date) AS cumulative_sum,
                dme.amount_total AS amount_total,
                dme.name AS name,
                dr.name AS requirement,
                rp.name AS full_name,
                dmed.origin_place AS origin_place,
                dmed.destiny AS destiny,
                dmed.reason AS reason
            FROM documental_mobility_expediture dme
            JOIN documental_mobility_expediture_detail dmed ON dme.id = dmed.documental_mobility_id
            LEFT JOIN budget b ON dme.budget_id = b.id
            LEFT JOIN cost_center cc ON b.cost_center_id = cc.id
            LEFT JOIN documental_requirements dr ON dme.requirement_id = dr.id
            LEFT JOIN res_users rs ON dme.full_name = rs.id
            LEFT JOIN res_partner rp ON rs.partner_id = rp.id
            WHERE dme.state != 'draft'
            ORDER BY dme.date DESC, dmed.date DESC;
        """
        self.env.cr.execute(query)
        return self.env.cr.dictfetchall()
