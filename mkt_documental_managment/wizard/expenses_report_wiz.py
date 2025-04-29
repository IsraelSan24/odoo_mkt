from odoo import _, fields, models
import datetime
import io as io
import base64

import logging
_logger = logging.getLogger(__name__)

class ExpensesReport(models.TransientModel):
    _name = 'expenses.report'
    _description = 'Expenses report'
    _inherit = ['report.formats']

    def change_state_name(self, state):
        final_state = ''
        if state == 'draft':
            final_state = _( 'Draft' )
        if state == 'executive':
            final_state = _( 'Executive' )
        if state == 'responsible':
            final_state = _( 'Responsible' )
        if state == 'intern_control':
            final_state = _( 'Intern control' )
        if state == 'administration':
            final_state = _( 'Administration' )
        if state == 'to_settle':
            final_state = _( 'To settle' )
        if state == 'settled':
            final_state = _( 'Settled' )
        if state == 'refused':
            final_state = _( 'Refused' )
        return final_state


    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')


    def _get_file_name(self, function_name, file_name=False):
        dic_name = super(ExpensesReport, self)._get_file_name(function_name, file_name=_( 'Expenses report' ))
        return dic_name


    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet( _('Expenses report') )

        ws.set_zoom(75)
        
        ws.set_row(5, 32.25)
        ws.set_column('B:B', 5.29)
        ws.set_column('C:C', 5.57)
        ws.set_column('D:D', 5)
        ws.set_column('E:E', 12.86)
        ws.set_column('F:F', 9)
        ws.set_column('G:G', 10.43)
        ws.set_column('H:H', 37.71)
        ws.set_column('I:I', 10.86)
        ws.set_column('J:J', 35.43)
        ws.set_column('K:K', 15)
        ws.set_column('L:L', 8.43)
        ws.set_column('M:M', 14.14)
        ws.set_column('N:N', 6.71)
        ws.set_column('O:O', 6.29)
        ws.set_column('P:P', 7.14)
        ws.set_column('Q:Q', 11.86)
        ws.set_column('R:R', 15.29)
        ws.set_column('S:S', 16)
        ws.set_column('T:T', 33.14)
        ws.set_column('U:U', 9.14)
        ws.set_column('V:V', 9.14)
        ws.set_column('W:W', 9.14)
        ws.set_column('X:X', 11.86)
        ws.set_column('Y:Y', 13.29)
        ws.set_column('Z:Z', 9.43)
        ws.set_column('AA:AA', 8.43)
        ws.set_column('AB:AB', 8.43)
        ws.set_column('AC:AC', 14.86)
        ws.set_column('AD:AD', 14.86)
        ws.set_column('AE:AE', 14.14)
        ws.set_column('AF:AF', 14.14)
        ws.set_column('AG:AG', 14.14)
        ws.set_column('AH:AH', 38.86)

        style1 = {
            'font_size': 18,
            'font_color': '#000000',
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
        }

        style2 = {
            'font_size': 11,
            'font_color': '#FFFFFF',
            'bg_color': '#FF3103',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'bold': True,
            'border_color': '#FFFFFF',
            'text_wrap': True,
        }
        
        style3 = {
            'font_size': 11,
            'bg_color': '#FFC19B',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        }
        
        style4 = {
            'font_size': 11,
            'bg_color': '#FFC19B',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': 'dd/mm/yyyy',
        }
        
        style5 = {
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
        }
        
        style6 = {
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': 'dd/mm/yyyy',
        }
        
        style7 = {
            'font_size': 11,
            'bg_color': '#FFFF00',
            'align': 'left',
            'valign': 'center',
            'border': 1,
        }
        style8 = {
            'font_size': 11,
            'bg_color': '#FFC19B',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00',
        }
    
        style9 = {
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00',
        }

        format1 = workbook.add_format(style1)
        format2 = workbook.add_format(style2)
        format3 = workbook.add_format(style3)
        format4 = workbook.add_format(style4)
        format5 = workbook.add_format(style5)
        format6 = workbook.add_format(style6)
        format7 = workbook.add_format(style7)
        format8 = workbook.add_format(style8)
        format9 = workbook.add_format(style9)

        company = self.env.user.company_id.logo
        if company:
            company_image = io.BytesIO(base64.b64decode(company))
            ws.write(1, 1, '')
            ws.insert_image(1, 1, 'image.png', {
                'image_data': company_image,
                'x_scale': 0.15,
                'y_scale': 0.15,
            })

        ws.merge_range('H2:L2', _('EXPENSES REPORT'), format1)

        ws.merge_range('B5:D5', _('PAYMENT DATE'), format2)
        ws.write('B6:B6', 'D', format2)
        ws.write('C6:C6', 'M', format2)
        ws.write('D6:D6', 'Y', format2)

        ws.merge_range('E5:E6', _('PT. N°'), format2)
        ws.merge_range('F5:F6', _('C.C. N°'), format2)
        ws.merge_range('G5:G6', _('CREDIT CARD'), format2)

        ws.merge_range('H5:J5', _('PAID TO'), format2)
        ws.write('H6:H6', _('Name'), format2)
        ws.write('I6:I6', _('Province'), format2)
        ws.write('J6:J6', _('Concept'), format2)

        ws.merge_range('K5:K6', _('REQUIREMENT'), format2)
        ws.merge_range('L5:L6', _('CURRENCY'), format2)
        ws.merge_range('M5:M6', _('REQUIREMENT AMOUNT'), format2)

        ws.merge_range('N5:P5', _('SETTLEMENT DATE'), format2)
        ws.write('N6:N6', _('D'), format2)
        ws.write('O6:O6', _('M'), format2)
        ws.write('P6:P6', _('A'), format2)

        ws.merge_range('Q5:T5', _('SETTLEMENT DETAIL'), format2)
        ws.write('Q6:Q6', _('Date'), format2)
        ws.write('R6:R6', _('Document type'), format2)
        ws.write('S6:S6', _('Document'), format2)
        ws.write('T6:T6', _('Reason'), format2)

        ws.merge_range('U5:AD5', _('SETTLEMENT AMOUNT DETAILS'), format2)
        ws.write('U6:U6', _('Amount'), format2)
        ws.write('V6:V6', _('Alternative Amount'), format2)
        ws.write('W6:W6', _('Vendor'), format2)
        ws.write('X6:X6', _('Total'), format2)
        ws.write('Y6:Y6', _('Refund to employee'), format2)
        ws.write('Z6:Z6', _('Refund to MKT'), format2)
        ws.write('AA6:AA6', 'IGV(%)', format2)
        ws.write('AB6:AB6', _('IGV'), format2)
        ws.write('AC6:AC6', 'Alternative IGV', format2)
        ws.write('AD6:AD6', 'B.I', format2)

        ws.merge_range('AE5:AE6', _('ORIGIN'), format2)
        ws.merge_range('AF5:AF6', _('STATE(RQ)'), format2)
        ws.merge_range('AG5:AG6', _('STATE(FL)'), format2)
        ws.merge_range('AH5:AH6', _('RESPONSIBLE'), format2)
        ws.autofilter('B6:AH6')


        records = self._get_query()
        row = 6
        line_aux = 'RQ-0'
        for line in records:
            if line_aux != line['requirement']:
                total_lines = line['settlement_lines'] or 0
                ws.write(row, 1, line['date'].day if line['date'] else '', format3)
                ws.write(row, 2, line['date'].month if line['date'] else '', format3)
                ws.write(row, 3, line['date'].year if line['date'] else '', format3)
                ws.write(row, 4, line['budget'], format3)
                ws.write(row, 5, line['cost_center'], format3)
                ws.write(row, 6, line['card_payment'] or ' ', format3)
                ws.write(row, 7, line['paid_to'], format3)
                ws.write(row, 8, line['province'] or ' ', format3)
                ws.write(row, 9, line['concept'], format3)
                ws.write(row, 10, line['requirement'], format3)
                ws.write(row, 11, line['currency'], format3)
                ws.write(row, 12, line['amount'], format8)
                ws.write(row, 13, line['settlement_date'].day if line['settlement_date'] else '', format3)
                ws.write(row, 14, line['settlement_date'].month if line['settlement_date'] else '', format3)
                ws.write(row, 15, line['settlement_date'].year if line['settlement_date'] else '', format3)
                ws.write(row, 16, line['settle_date'], format4)
                ws.write(row, 17, line['document_type'], format3)
                ws.write(row, 18, line['movement_document'], format3)
                ws.write(row, 19, str(line['partner']) + ' - ' + str(line['reason']), format3)
                ws.write(row, 20, line['settle_amount'], format8)
                ws.write(row, 21, line['alternative_amount'], format8)
                ws.write(row, 22, line['vendor'], format8)
                if line.get('alternative_amount'):
                    if total_lines == 0:
                        ws.write_formula(row, 23, '=SUM(V%s:V%s)' % (row + 1, row + 1), format8)
                    else:
                        ws.write_formula(row, 23, '=SUM(V%s:V%s)' % (row + 1, row + total_lines), format8)
                else:
                    if total_lines == 0:
                        ws.write_formula(row, 23, '=SUM(U%s:U%s)' % (row + 1, row + 1), format8)
                    else:
                        ws.write_formula(row, 23, '=SUM(U%s:U%s)' % (row + 1, row + total_lines), format8)
                ws.write(row, 24, '=X%s-M%s' % ( ( row + 1 ), ( row + 1 ) ), format8)
                ws.write(row, 25, '', format8)
                ws.write(row, 26, line['tax_percentage'], format3)
                ws.write(row, 27, line['settle_igv'], format8)
                ws.write(row, 28, line['alternative_igv'], format8)
                if line.get('alternative_amount') and line.get('alternative_igv'):
                    ws.write_formula(row, 29, '=(V%s-AC%s)' % (row + 1, row + 1), format8)
                elif line['income_tax'] and line['income_tax_id']:
                    ws.write_formula(
                        row,
                        29,
                        '=(U%s-AB%s) + %s*(U%s-AB%s)/100' % (
                            row + 1, row + 1,
                            line['income_tax_percentage'],
                            row + 1, row + 1
                        ),
                        format8
                    )
                else:
                    ws.write_formula(row, 29, '=(U%s-AB%s)' % (row + 1, row + 1), format8)
                ws.write(row, 30, line['origin'], format7 if line['origin'] else format3)
                ws.write(row, 31, self.change_state_name(line['requirement_state']), format3)
                ws.write(row, 32, self.change_state_name(line['settlement_state']), format3)
                ws.write(row, 33, line['responsible'], format3)
                row += 1
            else:
                ws.write(row, 1, '', format5)
                ws.write(row, 2, '', format5)
                ws.write(row, 3, '', format5)
                ws.write(row, 4, line['budget'], format5)
                ws.write(row, 5, line['cost_center'], format5)
                ws.write(row, 6, ' ', format5)
                ws.write(row, 7, line['paid_to'], format5)
                ws.write(row, 8, line['province'], format5)
                ws.write(row, 9, line['concept'], format5)
                ws.write(row, 10, line['requirement'], format5)
                ws.write(row, 11, '', format5)
                ws.write(row, 12, '', format9)
                ws.write(row, 13, '', format5)
                ws.write(row, 14, '', format5)
                ws.write(row, 15, '', format5)
                ws.write(row, 16, line['settle_date'], format6)
                ws.write(row, 17, line['document_type'], format5)
                ws.write(row, 18, line['movement_document'], format5)
                ws.write(row, 19, str(line['partner']) + ' - ' + str(line['reason']), format5)
                ws.write(row, 20, line['settle_amount'], format9)
                ws.write(row, 21, line['alternative_amount'], format8)
                ws.write(row, 22, line['vendor'], format9)
                ws.write(row, 23, '', format9)
                ws.write(row, 24, '=X%s-M%s' % ( ( row + 1 ), ( row + 1 ) ), format9)
                ws.write(row, 25, '', format9)
                ws.write(row, 26, line['tax_percentage'], format5)
                ws.write(row, 27, line['settle_igv'], format9)
                ws.write(row, 28, line['alternative_igv'], format9)
                if line.get('alternative_amount') and line.get('alternative_igv'):
                    ws.write_formula(row, 29, '=(V%s-AC%s)' % (row + 1, row + 1), format8)
                elif line['income_tax'] and line['income_tax_id']:
                    ws.write_formula(
                        row,
                        29,
                        '=(U%s-AB%s) + %s*(U%s-AB%s)/100' % (
                            row + 1, row + 1,
                            line['income_tax_percentage'],
                            row + 1, row + 1
                        ),
                        format8
                    )
                else:
                    ws.write_formula(row, 29, '=(U%s-AB%s)' % (row + 1, row + 1), format9)
                ws.write(row, 30, '', format5)
                ws.write(row, 31, '', format5)
                ws.write(row, 32, '', format5)
                ws.write(row, 33, '', format5)
                row += 1
            line_aux = line['requirement']


    def _get_query(self):
        query = """
            SELECT
                CASE
                    WHEN dr.unify = false THEN 'normal'
                    WHEN dr.unify = true THEN 'unified'
                END AS unified,
                COALESCE(dr.intern_control_signed_on, dr.settlement_intern_control_signed_on) AS date,
                b.name AS budget,
                cc.code AS cost_center,
                CASE
                    WHEN dr.card_payment = false THEN '-'
                    WHEN dr.card_payment = true THEN 'TC'
                END AS card_payment,
                rp.name AS paid_to,
                rpr.name AS province,
                dr.concept AS concept,
                dr.name AS requirement,
                dr.amount_currency_type AS currency,
                CASE
                    WHEN dr.amount_soles > 0 THEN dr.amount_soles
                    WHEN dr.amount_uss > 0 THEN dr.amount_uss
                END AS amount,
                COALESCE(dr.settlement_intern_control_signed_on, ds.intern_control_signed_on) AS settlement_date,
                s.date AS settle_date,
                slp.name AS document_type,
                COALESCE(s.movement_number, s.document) AS movement_document,
                s.partner AS partner,
                s.reason AS reason,
                s.settle_amount_sum AS settle_amount,
                s.alternative_amount AS alternative_amount,
                s.vendor_sum AS vendor,
                s.settle_igv_sum AS settle_igv,
                s.alternative_igv AS alternative_igv,
                tt.percentage AS tax_percentage,
                s.income_tax AS income_tax,
                s.income_tax_id AS income_tax_id,
	            tt2.percentage AS income_tax_percentage,
                CAST((s.settle_amount_sum - s.settle_igv_sum) AS numeric(10,2)) AS amount_line,
                dr.requirement_state AS requirement_state,
                dr.settlement_state AS settlement_state,
                rp2.name AS responsible,
                dr.settlement_total_lines AS settlement_lines,
                dr2.name AS origin
            FROM documental_requirements AS dr
                LEFT JOIN budget AS b ON b.id=dr.budget_id
                LEFT JOIN cost_center AS cc ON cc.id=b.cost_center_id
                LEFT JOIN res_partner AS rp ON rp.id=dr.paid_to
                LEFT JOIN res_province AS rpr ON rpr.id=rp.province_id
                LEFT JOIN documental_settlements AS ds ON dr.id=ds.requirement_id
                LEFT JOIN settlement AS s ON s.requirement_id=dr.id
                LEFT JOIN settlement_line_type AS slp ON slp.id=s.document_type_id
                LEFT JOIN tax_taxes AS tt ON tt.id=s.tax_id
                LEFT JOIN res_users AS ru ON ru.id=dr.full_name
                LEFT JOIN res_partner AS rp2 ON rp2.id=ru.partner_id
                LEFT JOIN documental_requirements AS dr2 ON dr2.id=dr.refund_requirement_id
                LEFT JOIN tax_taxes AS tt2 ON tt2.id=s.income_tax_id
                WHERE (dr.intern_control_signed_on IS NOT NULL OR dr.settlement_intern_control_signed_on IS NOT NULL) AND dr.active != False
            ORDER BY dr.name DESC, s.date ASC
        """
        self._cr.execute(query)
        res_query = self._cr.dictfetchall()
        return res_query
