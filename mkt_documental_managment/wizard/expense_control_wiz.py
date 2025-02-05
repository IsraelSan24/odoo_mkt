from odoo import _, api, fields, models
import datetime
import io as io
import base64

import logging
_logger = logging.getLogger(__name__)

class ExpenseControl(models.TransientModel):
    _name = 'expense.control'
    _description = 'Expense Control Report'
    _inherit = ['report.formats']

    province = fields.Selection(selection=[('lima','Lima'),('province','Province')], string='Lima/Province')
    date_from = fields.Datetime(string='Date from')
    date_to = fields.Datetime(string='Date to')

    def change_state_name(self, state):
        final_state = ''
        if state == 'draft':
            final_state = _('Draft')
        elif state == 'waiting_boss_validation':
            final_state = _('Waiting Boss Validation')
        elif state == 'waiting_intern_control_validation':
            final_state = _('Waiting Intern Control Validation')
        elif state == 'waiting_administration_validation':
            final_state = _('Waiting Administration Validation')
        elif state == 'settled':
            final_state = _('Settled')
        else:
            final_state = _('Refused')
        return final_state


    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')
    

    def _get_file_name(self, function_name, file_name=False):
        if self.province == 'lima':
            dic_name = super(ExpenseControl, self)._get_file_name(function_name, file_name=_('Expense Control Report: Lima'))
        if self.province == 'province':
            dic_name = super(ExpenseControl, self)._get_file_name(function_name, file_name=_('Expense Control Report: Province'))
        return dic_name


    def _get_datas_report_xlsx(self, workbook):
        if self.province == 'lima':
            ws = workbook.add_worksheet(_('Lima Report'))
        if self.province == 'province':
            ws = workbook.add_worksheet(_('Province Report'))

        style1 = {
            'font_size':18,
            'font_color':'#000000',
            'align':'center',
            'valign':'vcenter',
            'bold':True,
        }
        style2 = {
            'font_size':11,
            'font_color':'#FFFFFF',
            'bg_color':'#FF3103',
            'align':'center',
            'valign':'vcenter',
            'border':2,
            'bold':True,
            'border_color':'#FFFFFF',
        }
        style3 = {
            'font_size':11,
            'font_color':'#FFFFFF',
            'bg_color':'#FF3103',
            'align':'center',
            'valign':'vcenter',
            'left':2,
            'top':2,
            'right':2,
            'bold':True,
            'border_color':'#FFFFFF',
        }
        style4 = {
            'font_size':11,
            'font_color':'#FFFFFF',
            'bg_color':'#FF3103',
            'align':'center',
            'valign':'vcenter',
            'left':2,
            'right':2,
            'bottom':2,
            'bold':True,
            'border_color':'#FFFFFF',
        }
        style5 = {
            'font_size':11,
            'align':'center',
            'valign':'vcenter',
            'border':1,
            'num_format':'dd/mm/yyyy',
        }
        style6 = {
            'font_size':11,
            'align':'center',
            'valign':'vcenter',
            'border':1,
        }
        style7 = {
            'font_size':11,
            'bg_color':'#FFC19B',
            'align':'center',
            'valign':'vcenter',
            'border':1,
        }
        style8 = {
            'font_size':11,
            'bg_color':'#FFC19B',
            'align':'center',
            'valign':'vcenter',
            'border':1,
            'num_format':'dd/mm/yyyy',
        }
        style9 = {
            'font_size':11,
            'bg_color':'#F59751',
            'align':'center',
            'valign':'vcenter',
            'border':1,
        }
        style10 = {
            'font_size':11,
            'bg_color':'#F59751',
            'align':'center',
            'valign':'vcenter',
            'border':1,
            'num_format':'dd/mm/yyyy',
        }
        style11 = {
            'font_size':11,
            'bg_color':'#FFC19B',
            'align':'center',
            'valign':'vcenter',
            'border':1,
            'num_format': '#,##0.00',
        }
        style12 = {
            'font_size':11,
            'align':'center',
            'valign':'vcenter',
            'border':1,
            'num_format': '#,##0.00',
        }

        stl1 = workbook.add_format(style1)
        stl2 = workbook.add_format(style2)
        stl3 = workbook.add_format(style3)
        stl4 = workbook.add_format(style4)
        stl5 = workbook.add_format(style5)
        stl6 = workbook.add_format(style6)
        stl7 = workbook.add_format(style7)
        stl8 = workbook.add_format(style8)
        stl9 = workbook.add_format(style9)
        stl10 = workbook.add_format(style10)
        stl11 = workbook.add_format(style11)
        stl12 = workbook.add_format(style12)

        ws.set_column('B:B', 9)
        ws.set_column('C:C', 9)
        ws.set_column('D:D', 9)
        ws.set_column('E:E', 14)
        ws.set_column('F:F', 7)
        ws.set_column('G:G', 9)
        ws.set_column('H:H', 45)
        ws.set_column('I:I', 12)
        ws.set_column('J:J', 42)
        ws.set_column('K:K', 15)
        ws.set_column('L:L', 8)
        ws.set_column('M:M', 9)
        ws.set_column('N:N', 6)
        ws.set_column('O:O', 6)
        ws.set_column('P:P', 8)
        ws.set_column('Q:Q', 11)
        ws.set_column('R:R', 31)
        ws.set_column('S:S', 13)
        ws.set_column('T:T', 40)
        ws.set_column('U:U', 12)
        ws.set_column('V:V', 10)
        ws.set_column('W:W', 16)
        ws.set_column('X:X', 16)
        ws.set_column('Y:Y', 12)
        ws.set_column('Z:Z', 8)
        ws.set_column('AA:AA', 12)
        ws.set_column('AB:AB', 18)
        ws.set_column('AC:AC', 30)
        ws.set_column('AD:AD', 13)

        company = self.env.user.company_id.logo
        if company:
            company_image = io.BytesIO(base64.b64decode(company))
            ws.write(1, 1, '')
            ws.insert_image(1, 1, "image.png", {
                'image_data': company_image,
                'x_scale': 0.15,
                'y_scale': 0.15,
            })

        ws.merge_range('H2:L2', _('EXPENSE CONTROL REPORT'), stl1)

        ws.merge_range('B5:D5', _('PAYMENT REQUIRED DATE'), stl2)
        ws.write('E5:E5', _('N°'), stl3)
        ws.write('F5:F5', _('N°'), stl3)
        ws.write('G5:G5', _('CARD'), stl3)
        # ws.merge_range('H5:I5', _('PAID TO'), stl2)
        ws.merge_range('H5:J5', _('PAID TO'), stl2)
        ws.merge_range('K5:K6', _('REQUIREMENT'), stl2)
        ws.merge_range('L5:L6', _('CURRENCY'), stl2)
        ws.write('M5:M5', _('REQUIREMENT'), stl3)
        ws.merge_range('N5:P5', _('SETTLE DATE'), stl2)
        ws.merge_range('Q5:U5', _('SETTLE DETAILS'), stl2)
        ws.merge_range('V5:AC5', _('SETTLE AMOUNT DETAILS'), stl2)
        ws.merge_range('AD5:AD6', _('OBSERVATION'), stl2)
        ws.merge_range('AE5:AE6', _('RESPONSIBLE'), stl2)
        ws.write('AF5:AF5', _('REVIEW'), stl3)
        # ws.merge_range('AF5:AF6', _('EXONERATED'), stl12)

        ws.write('B6:B6', _('Day'), stl4)
        ws.write('C6:C6', _('Month'), stl4)
        ws.write('D6:D6', _('Year'), stl4)
        ws.write('E6:E6', _('BUDGET'), stl4)
        ws.write('F6:F6', _('COST CENTER'), stl4)
        ws.write('G6:G6', _('CREDIT'), stl4)
        ws.write('H6:H6', _('NAME'), stl4)
        ws.write('I6:I6', _('PROVINCE'), stl4)
        ws.write('J6:J6', _('CONCEPT'), stl4)
        # ws.write('L6:L6', _('CURRENCY'), stl4)
        ws.write('M6:M6', _('AMOUNT'), stl4)
        ws.write('N6:N6', _('Day'), stl4)
        ws.write('O6:O6', _('Month'), stl4)
        ws.write('P6:P6', _('Year'), stl4)
        ws.write('Q6:Q6', _('Date'), stl4)
        ws.write('R6:R6', _('Document type'), stl4)
        ws.write('S6:S6', _('Document'), stl4)
        ws.write('T6:T6', _('Reason'), stl4)
        ws.write('U6:U6', _('Amount'), stl4)
        ws.write('V6:V6', _('Total'), stl4)
        ws.write('W6:W6', _('Refund to Employee'), stl4)
        ws.write('X6:X6', _('Refund to MKT'), stl4)
        ws.write('Y6:Y6', _('Consume surcharge'), stl4)
        ws.write('Z6:Z6', _('Exon.'), stl4)
        ws.write('AA6:AA6', _('IGV Amount'), stl4)
        ws.write('AB6:AB6', _('IGV(%)'), stl4)
        ws.write('AC6:AC6', _('Tax Base'), stl4)
        ws.write('AF6:AF6', _('BUDGET'), stl4)
        ws.autofilter('B6:AF6')

        records = self._get_query()
        row = 6
        line_aux = datetime.date.today()
        for line in records:
            if line_aux != line['date']:
                total_lines = line['sd_total_lines'] or 0
                ws.write(row, 1, line['date'].day, stl7)
                ws.write(row, 2, line['date'].month, stl7)
                ws.write(row, 3, line['date'].year, stl7)
                ws.write(row, 4, line['budget'], stl7)
                ws.write(row, 5, line['cost_center'], stl7)
                ws.write(row, 6, 'TC' if line['card_payment'] == True else '', stl7)
                ws.write(row, 7, line['paid_to'], stl7)
                ws.write(row, 8, line['province'], stl7)
                ws.write(row, 9, line['rq_concept'], stl7)
                ws.write(row, 10, line['rq_name'], stl7)
                ws.write(row, 11, line['currency'], stl7)
                ws.write(row, 12, line['rounded_amount'], stl11)
                if line['ds_signed_date']:
                    ws.write(row, 13, line['ds_signed_date'].day, stl7)
                    ws.write(row, 14, line['ds_signed_date'].month, stl7)
                    ws.write(row, 15, line['ds_signed_date'].year, stl7)
                else:
                    ws.write(row, 13, '', stl7)
                    ws.write(row, 14, '', stl7)
                    ws.write(row, 15, '', stl7)
                ws.write(row, 16, line['dsd_date'], stl8)
                ws.write(row, 17, line['dsd_document_type'], stl7)
                ws.write(row, 18, line['dsd_movement_number'] if line['dsd_movement_number'] else line['dsd_document'], stl7)
                ws.write(row, 19, str(line['dsd_partner']) + ' - ' + str(line['dsd_reason']), stl7)
                ws.write(row, 20, line['dsd_amount'], stl11)
                if total_lines == 0:
                    ws.write_formula(row, 21, '=SUM(U%s:U%s)' % ( ( row + 1 ),( row + 1 ) + total_lines ), stl11)
                else:
                    ws.write_formula(row, 21, '=SUM(U%s:U%s)-%s' % ( ( row + 1 ),( row + 1 ) + total_lines - 1, line['total_return'] ), stl11)
                if line['ds_total_amount'] and line['rounded_amount'] and line['ds_total_amount'] > line['rounded_amount']:
                    ws.write(row, 22, round( line['ds_total_amount'] - line['rounded_amount'],2 ), stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl11)
                    ws.write(row, 23, 0, stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl11)
                else:
                    ws.write(row, 22, '', stl7)
                    ws.write(row, 23, '', stl7)
                if line['dsd_id']:
                    detail_line = self.env['settlement.detail.line'].search([('settlement_detail','=',line['dsd_id']),('igv_tax','=','consumption_surcharge')]).mapped('unit_price')
                    exonerated = self.env['settlement.detail.line'].search([('settlement_detail','=',line['dsd_id']),('igv_tax','=','exonerated')]).mapped('unit_price')
                    ws.write(row, 24, sum(detail_line), stl11)
                    ws.write(row, 25, sum(exonerated), stl11)
                else:
                    ws.write(row, 24, 0, stl11)
                    ws.write(row, 25, 0, stl11)
                if line['dsd_id'] and line['dsd_amount'] == sum(exonerated):
                    ws.write(row, 26, 0, stl11)
                else:
                    ws.write(row, 26, '=(U%s-Y%s-Z%s-AC%s)' % ( ( row + 1 ), ( row + 1 ), ( row + 1 ), ( row + 1)), stl11)
                ws.write(row, 27, line['tax_perc'], stl11)
                if line['dsd_id'] and line['dsd_amount'] == sum(exonerated):
                    ws.write_formula(row, 28, '=U%s+Y%s' % ( ( row + 1 ), ( row + 1 ) ), stl11)
                else:
                    if line['dsd_igv_included'] == True:
                        ws.write_formula(row, 28, '=(U%s-Z%s)/(1+AB%s/100)+Y%s' % ( ( row + 1 ), ( row + 1 ), ( row + 1 ), ( row + 1 )), stl11)
                    else:
                        ws.write_formula(row, 28, '=(U%s-Y%s-Z%s)/(1+AB%s/100)+Y%s' % ( ( row + 1 ), ( row + 1 ), ( row + 1 ), ( row + 1 ), ( row + 1 )), stl11)
                ws.write(row, 29, self.change_state_name(line['ds_state']), stl7)
                ws.write(row, 30, line['responsible'], stl7)
                ws.write(row, 31, 'COB' if line['dsd_review'] == True else '0', stl7)
                row += 1
            else:
                ws.write(row, 1, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 2, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 3, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 4, line['budget'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 5, line['cost_center'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 6, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 7, line['paid_to'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 8, line['province'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 9, line['rq_concept'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 10, line['rq_name'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 11, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 12, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 13, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 14, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 15, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 16, line['dsd_date'], stl10 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl5)
                ws.write(row, 17, line['dsd_document_type'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 18, line['dsd_movement_number'] if line['dsd_movement_number'] else line['dsd_document'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 19, str(line['dsd_partner']) + ' - ' + str(line['dsd_reason']), stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 20, line['dsd_amount'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                ws.write(row, 21, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                if line['rounded_amount'] and line['ds_total_amount'] and line['dsd_document_type'] == 'DEVOLUCIÓN':
                    ws.write(row, 22, round( line['ds_total_amount'] - line['rounded_amount'],2 ) if line['ds_total_amount'] > line['rounded_amount'] else 0, stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                    ws.write(row, 23, round( line['rounded_amount'] - line['ds_total_amount'],2 ) if line['rounded_amount'] > line['ds_total_amount'] else 0, stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                else:
                    ws.write(row, 22, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                    ws.write(row, 23, '', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                if line['dsd_id']:
                    detail_line = self.env['settlement.detail.line'].search([('settlement_detail','=',line['dsd_id']),('igv_tax','=','consumption_surcharge')]).mapped('unit_price')
                    exonerated = self.env['settlement.detail.line'].search([('settlement_detail','=',line['dsd_id']),('igv_tax','=','exonerated')]).mapped('unit_price')
                    ws.write(row, 24, sum(detail_line), stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                    ws.write(row, 25, sum(exonerated), stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                else:
                    ws.write(row, 24, 0, stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                    ws.write(row, 25, 0, stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                if line['dsd_id'] and line['dsd_amount'] == sum(exonerated):
                    ws.write(row, 26, 0, stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                else:
                    ws.write(row, 26, '=(U%s-Y%s-Z%s-AC%s)' % ( ( row + 1 ), ( row + 1 ), ( row + 1 ), ( row + 1)), stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                ws.write(row, 27, line['tax_perc'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                if line['dsd_id'] and line['dsd_amount'] == sum(exonerated):
                    ws.write_formula(row, 28, '=U%s+Y%s' % ( ( row + 1 ), ( row + 1 ) ), stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                else:
                    if line['dsd_igv_included'] == True:
                        ws.write_formula(row, 28, '=(U%s-Z%s)/(1+AB%s/100)+Y%s' % ( ( row + 1 ), ( row + 1 ), ( row + 1 ), ( row + 1 )), stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                    else:
                        ws.write_formula(row, 28, '=(U%s-Y%s-Z%s)/(1+AB%s/100)+Y%s' % (( row + 1 ), ( row + 1 ), ( row + 1 ), ( row + 1 ), ( row + 1 )), stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl12)
                ws.write(row, 29, self.change_state_name(line['ds_state']), stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 30, line['responsible'], stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                ws.write(row, 31, 'COB' if line['dsd_review'] == True else '0', stl9 if line['dsd_document_type'] and line['dsd_document_type'] == 'DEVOLUCIÓN' else stl6)
                row += 1
            line_aux = line['date']


    def _get_query(self):
        date_from = self.date_from
        date_to = self.date_to
        if self.province == 'lima':
            where = "AND (rpr.name = 'Lima' OR rpr.name IS NULL)"
        elif self.province == 'province':
            where = "AND rpr.name != 'Lima'"
        else:
            where = ""
        query = """
            SELECT
                dr.date AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' AS creation_date,
                dr.intern_control_signed_on AS date,
                b.name AS budget,
                cc.name AS cc_name,
                cc.code AS cost_center,
                dr.card_payment AS card_payment,
                rp2.name AS paid_to,
                rpr.name AS province,
                dr.concept AS rq_concept,
                dr.name AS rq_name,
                ds.total_lines AS sd_total_lines,
                CASE
                    WHEN dr.amount_currency_type = 'soles' THEN 'S/'
                    WHEN dr.amount_currency_type = 'dolares' THEN '$$'
                END AS currency,
                CASE
                    WHEN dr.amount_soles > 0 THEN dr.amount_soles
                    WHEN dr.amount_uss > 0 THEN dr.amount_uss
                END AS rounded_amount,
                ds.name AS settlement,
                ds.create_date AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' AS ds_date,
                ds.intern_control_signed_on AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' AS ds_signed_date,
                dsd.date AS dsd_date,
                dsd.partner AS dsd_partner,
                slp.name AS dsd_document_type,
                ds.total_return AS total_return,
                slp.is_return AS is_return,
                dsd.document AS dsd_document,
                dsd.movement_number AS dsd_movement_number,
                dsd.reason AS dsd_reason,
                CAST(dsd.amount AS numeric(10,2)) AS dsd_amount,
                CAST(ds.total_import AS numeric(10,2)) AS ds_total_amount,
                (SELECT COALESCE(SUM(igv), 0) FROM settlement_detail_line WHERE settlement_detail = dsd.id) AS dsd_igv_total,
                tt.percentage AS tax_perc,
                (SELECT COALESCE(SUM(base_amount), 0) FROM settlement_detail_line WHERE settlement_detail = dsd.id) AS dsd_total_amount_base,
                ds.state AS ds_state,
                rp.name AS responsible,
                dsd.review_in_quotation AS dsd_review,
	            dsd.id AS dsd_id,
	            dsd.igv_included AS dsd_igv_included,
                COALESCE(dr.intern_control_received, dr.boss_signed_on) AS received_by_intern_control,
	            ds.id AS ds_id
            FROM documental_requirements AS dr
                LEFT JOIN budget AS b ON b.id=dr.budget_id
                LEFT JOIN res_partner AS rp2 ON rp2.id=dr.paid_to
                LEFT JOIN cost_center AS cc ON cc.id=b.cost_center_id
                LEFT JOIN res_users AS ru ON ru.id=dr.full_name
                LEFT JOIN res_partner AS rp ON rp.id=ru.partner_id
                LEFT JOIN documental_settlements AS ds ON dr.id=ds.requirement_id
                LEFT JOIN documental_settlements_detail AS dsd ON ds.id=dsd.documental_settlement_id
                LEFT JOIN tax_taxes AS tt ON tt.id=dsd.tax_igv_id
                LEFT JOIN settlement_line_type AS slp ON slp.id=dsd.document_type
                LEFT JOIN res_province AS rpr ON rpr.id=rp2.province_id
            WHERE dr.state IN ('waiting_administration_validation','to_settle','settled') AND dr.intern_control_signed_on IS NOT NULL {}
                AND COALESCE(dr.intern_control_received, dr.boss_signed_on) >= '{}'
                AND COALESCE(dr.intern_control_received, dr.boss_signed_on) <= '{}'
            ORDER BY dr.date DESC, dsd.date ASC
        """.format(where, date_from if date_from else '2023-01-01', date_to if date_to else '2050-01-01')
        self._cr.execute(query)
        res_query = self._cr.dictfetchall()
        return res_query
