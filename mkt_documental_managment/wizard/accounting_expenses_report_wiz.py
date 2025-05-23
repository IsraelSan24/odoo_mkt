from odoo import _, fields, models
import datetime
import io as io
import base64

import logging
_logger = logging.getLogger(__name__)

class AccountingExpensesReport(models.TransientModel):
    _name = 'accounting.expenses.report'
    _description = 'Accounting expenses report'
    _inherit = ['report.formats']
    
    date_from = fields.Date(string="Start Date", required=True)
    date_to = fields.Date(string="End Date", required=True)

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
        dic_name = super(AccountingExpensesReport, self)._get_file_name(function_name, file_name=_( 'MKT Accounting Expenses report' ))
        return dic_name


    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet( _('Accounting expenses report') )

        ws.set_zoom(75)
        
        ws.set_row(5, 32.25)
        ws.set_column('B:B', 11.29)
        ws.set_column('C:C', 11.29)
        ws.set_column('D:D', 6.43)
        ws.set_column('E:E', 14.14)
        ws.set_column('F:F', 9.86)
        ws.set_column('G:G', 13.14)
        ws.set_column('H:H', 40.43)
        ws.set_column('I:I', 19.86)
        ws.set_column('J:J', 53.57)
        ws.set_column('K:K', 15.43)
        ws.set_column('L:L', 11.86)
        ws.set_column('M:M', 15)
        ws.set_column('N:N', 14)
        ws.set_column('O:O', 11.29)
        ws.set_column('P:P', 5.43)
        ws.set_column('Q:Q', 20.14)
        ws.set_column('R:R', 30.43)
        ws.set_column('S:S', 9.86)
        ws.set_column('T:T', 15.86)
        ws.set_column('U:U', 15.86)
        ws.set_column('V:V', 56.57)
        ws.set_column('W:W', 15.29)
        ws.set_column('X:X', 14.29)
        ws.set_column('Y:Y', 14.29)
        ws.set_column('Z:Z', 45.43)

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
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00',
        }
    
        style9 = {
            'font_size': 11,
            'align': 'right',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00',
        }
        
        style10 = {
            'font_size': 11,
            'bg_color': '#FFC19B',
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
        }

        style11 = {
            'font_size': 11,
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
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
        format10 = workbook.add_format(style10)
        format11 = workbook.add_format(style11)

        company = self.env.user.company_id.logo
        # if company:
        #     company_image = io.BytesIO(base64.b64decode(company))
        #     ws.write(1, 1, '')
        #     ws.insert_image(1, 1, 'image.png', {
        #         'image_data': company_image,
        #         'x_scale': 0.15,
        #         'y_scale': 0.15,
        #     })

        ws.merge_range('H2:L2', _('ACCOUNTING EXPENSES REPORT'), format1)

        ws.merge_range('B5:B6', _('DATE'), format2)
        ws.merge_range('C5:C6', _('PT. N°'), format2)
        ws.merge_range('D5:D6', _('C.C. N°'), format2)
        ws.merge_range('E5:E6', _('CREDIT CARD'), format2)

        ws.merge_range('F5:J5', _('PAID TO'), format2)
        ws.write('F6', _('DNI'), format2)
        ws.write('G6', _('RUC'), format2)
        ws.write('H6', _('NAME'), format2)
        ws.write('I6', _('PROVINCE'), format2)
        ws.write('J6', _('CONCEPT'), format2)

        ws.merge_range('K5:K6', _('REQUIREMENT'), format2)
        ws.merge_range('L5:L6', _('CURRENCY'), format2)
        ws.merge_range('M5:M6', _('REQUIREMENT AMOUNT'), format2)
        ws.merge_range('N5:N6', _('SETTLEMENT DATE'), format2)

        ws.merge_range('O5:W5', _('SETTLEMENT DETAIL'), format2)
        ws.write('O6', _('D/DOC'), format2)
        ws.write('P6', _('DT'), format2)
        ws.write('Q6', _('DOCUMENT N°'), format2)
        ws.write('R6', _('DOCUMENT TYPE'), format2)
        ws.write('S6', _('DNI'), format2)
        ws.write('T6', _('RUC'), format2)
        ws.write('U6', _('ACCOUNT'), format2)
        ws.write('V6', _('REASON'), format2)
        ws.write('W6', _('AMOUNT'), format2)
        ws.merge_range('X5:X6', _('STATE(RQ)'), format2)
        ws.merge_range('Y5:Y6', _('STATE(FL)'), format2)
        ws.merge_range('Z5:Z6', _('RESPONSIBLE'), format2)

        ws.autofilter('B6:Z6')

        records = self._get_query()
        row = 6
        line_aux = 'RQ-0'
        for line in records:
            if line_aux != line['requirement']:
                ws.write(row, 1, line['date'], format4)
                ws.write(row, 2, line['budget'], format3)
                ws.write(row, 3, line['cost_center'], format3)
                ws.write(row, 4, line['card_payment'] or ' ', format3)
                ws.write(row, 5, line['dni_ruc_requirement'] if len(line['dni_ruc_requirement'] or '') == 8 else '', format3)
                ws.write(row, 6, line['dni_ruc_requirement'] if len(line['dni_ruc_requirement'] or '') != 8 else '', format3)
                ws.write(row, 7, line['paid_to'], format10)
                ws.write(row, 8, (line['province'] or '').upper(), format3)
                ws.write(row, 9, line['concept'], format10)
                ws.write(row, 10, line['requirement'], format3)
                ws.write(row, 11, line['currency'], format3)
                ws.write(row, 12, line['amount'], format8)
                ws.write(row, 13, line['settlement_date'], format4)
                ws.write(row, 14, line['settle_date'], format4)
                ws.write(row, 15, line['short_name'], format3)
                ws.write(row, 16, line['movement_document'], format3)
                ws.write(row, 17, line['document_type'], format3)
                ws.write(row, 18, line['dni_ruc_settlement'] if len(line['dni_ruc_settlement'] or '') == 8 else '', format3)
                ws.write(row, 19, line['dni_ruc_settlement'] if len(line['dni_ruc_settlement'] or '') != 8 else '', format3)
                ws.write(row, 20, line['accounting_account'], format3)
                ws.write(row, 21, str(line['partner']) + ' - ' + str(line['reason']), format10)
                ws.write(row, 22, line['settle_amount'], format8)
                ws.write(row, 23, self.change_state_name(line['requirement_state']), format3)
                ws.write(row, 24, self.change_state_name(line['settlement_state']), format3)
                ws.write(row, 25, line['responsible'], format3)
            else:
                ws.write(row, 1, '', format5)
                ws.write(row, 2, line['budget'], format5)
                ws.write(row, 3, line['cost_center'], format5)
                ws.write(row, 4, ' ', format5)
                ws.write(row, 5, line['dni_ruc_requirement'] if len(line['dni_ruc_requirement'] or '') == 8 else '', format5)
                ws.write(row, 6, line['dni_ruc_requirement'] if len(line['dni_ruc_requirement'] or '') != 8 else '', format5)
                ws.write(row, 7, line['paid_to'], format11)
                ws.write(row, 8, (line['province'] or '').upper(), format5)
                ws.write(row, 9, line['concept'], format11)
                ws.write(row, 10, line['requirement'], format5)
                ws.write(row, 11, '', format5)
                ws.write(row, 12, '', format9)
                ws.write(row, 13, '', format9)
                ws.write(row, 14, line['settle_date'], format6)
                ws.write(row, 15, line['short_name'], format5)
                ws.write(row, 16, line['movement_document'], format5)
                ws.write(row, 17, line['document_type'], format5)
                ws.write(row, 18, line['dni_ruc_settlement'] if len(line['dni_ruc_settlement'] or '') == 8 else '', format3)
                ws.write(row, 19, line['dni_ruc_settlement'] if len(line['dni_ruc_settlement'] or '') != 8 else '', format3)
                ws.write(row, 20, line['accounting_account'], format5)
                ws.write(row, 21, str(line['partner']) + ' - ' + str(line['reason']), format11)
                ws.write(row, 22, line['settle_amount'], format9)
                ws.write(row, 23, '', format9)
                ws.write(row, 24, '', format9)
                ws.write(row, 25, '', format9)
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
                s.accounting_account AS accounting_account,
                slp.name AS document_type,
                slp.short_name AS short_name,
                COALESCE(s.movement_number, s.document) AS movement_document,
                s.partner AS partner,
                s.reason AS reason,
                s.dni_ruc AS dni_ruc_settlement,
                s.settle_amount AS settle_amount,
                s.settle_igv AS settle_igv,
                tt.percentage AS tax_percentage,
                s.income_tax AS income_tax,
                s.income_tax_id AS income_tax_id,
                tt2.percentage AS income_tax_percentage,
                CAST((s.settle_amount - s.settle_igv) AS numeric(10,2)) AS amount_line,
                dr.requirement_state AS requirement_state,
                dr.settlement_state AS settlement_state,
                rp2.name AS responsible,
                dr.settlement_total_lines AS settlement_lines,
                dr2.name AS origin,
                dr.dni_or_ruc AS dni_ruc_requirement
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
            WHERE (dr.intern_control_signed_on IS NOT NULL OR dr.settlement_intern_control_signed_on IS NOT NULL) 
                AND dr.active != False
                AND COALESCE(dr.intern_control_signed_on, dr.settlement_intern_control_signed_on) BETWEEN %s AND %s
            ORDER BY dr.name DESC, s.date ASC
        """

        params = (self.date_from, self.date_to)

        self._cr.execute(query, params)
        res_query = self._cr.dictfetchall()
        return res_query
