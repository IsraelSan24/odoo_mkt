from odoo import _, models


class BankReport(models.TransientModel):
    _name = 'bank.report'
    _description = 'Bank report'
    _inherit = ['report.formats']

    def change_state_name(self, state):
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


    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')


    def _get_file_name(self, function_name, file_name=False):
        dic_name = super(BankReport, self)._get_file_name(function_name, file_name=_('Bank report'))
        return dic_name


    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Bank report'))
        
        ws.set_zoom(70)
        ws.set_column('A:A', 20.86)
        ws.set_column('B:B', 19.14)
        ws.set_column('C:C', 10.86)
        ws.set_column('D:D', 19.57)
        ws.set_column('E:E', 19.57)
        ws.set_column('F:F', 45.71)
        ws.set_column('F:F', 42.57)
        ws.set_column('G:G', 42.57)
        ws.set_column('H:H', 20.43)
        ws.set_column('I:I', 15.43)
        ws.set_column('J:J', 13.43)
        ws.set_column('K:K', 13.43)
        ws.set_column('L:L', 23.14)
        ws.set_column('M:M', 16)
        ws.set_column('N:N', 19)
        ws.set_column('O:O', 14)
        ws.set_column('P:P', 18.14)
        ws.set_column('Q:Q', 57.57)
        ws.set_column('R:R', 31)
        ws.set_column('S:S', 21.29)
        ws.set_column('T:T', 16.43)
        ws.set_column('U:U', 16)
        ws.set_column('V:V', 16)
        ws.set_column('W:W', 16.57)
        ws.set_column('X:X', 19)
        ws.set_column('Y:Y', 40.43)
        ws.set_column('Z:Z', 33)
        ws.set_column('AA:AA', 19)
        ws.set_column('AB:AB', 28)
        ws.set_column('AV:AC', 22.29)
        ws.set_column('AD:AD', 21.79)
        ws.freeze_panes(2,1)

        style1 = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'align': 'center',
            'border': 2,
            'bold': True,
        }
        style2 = {
            'font_color': '#000000',
            'bg_color': '#9CADCE',
            'align': 'center',
            'border': 2,
            'bold': True,
        }
        style3 = {
            'font_color': '#000000',
            'bg_color': '#9CADCE',
            'align': 'left',
            'border': 1,
            'bold': True
        }
        style4 = {
            'font_color': '#000000',
            'bg_color': '#9CADCE',
            'align': 'center',
            'border': 1,
            'bold': True
        }
        style5 = {
            'font_color': '#000000',
            'bg_color': '#9CADCE',
            'align': 'center',
            'border': 1,
            'bold': True,
            'num_format': 'dd/mm/yy',
        }
        style6 = {
            'font_color': '#000000',
            'bg_color': '#9CADCE',
            'align': 'center',
            'border': 1,
            'bold': True,
            'num_format': '#,##0.00',
        }
        style7 = {
            'font_color': '#000000',
            'bg_color': '#D1CFE2',
            'align': 'center',
            'border': 1,
            'bold': True,
        }
        style8 = {
            'font_color': '#000000',
            'bg_color': '#D1CFE2',
            'align': 'center',
            'border': 1,
            'bold': True,
            'num_format': '#,##0.00'
        }
        style9 = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'border': 1,
            'bold': True,
            'align': 'center'
        }
        style10 = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'border': 1,
            'bold': True,
            'align': 'center',
            'num_format': '#,##0.00'
        }
        style11 = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'border': 1,
            'bold': True,
            'align': 'center',
            'num_format': 'dd/mm/yy',
        }
        style12 = {
            'font_color': '#000000',
            'bg_color': '#D1CFE2',
            'align': 'left',
            'border': 1,
            'bold': True,
        }
        style13 = {
            'font_color': '#000000',
            'bg_color': '#FFFFFF',
            'border': 1,
            'bold': True,
            'align': 'left'
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
        stl13 = workbook.add_format(style13)
        
        ws.write('A2:A2', _('REQUIREMENT'), stl1)
        ws.write('B2:B2', _('BUDGET'), stl1)
        ws.write('C2:C2', _('CC'), stl1)
        ws.write('D2:D2', _('DNI'), stl1)
        ws.write('E2:E2', _('RUC'), stl1)
        ws.write('F2:F2', _('PAID TO'), stl1)
        ws.write('G2:G2', _('CONCEPT'), stl1)
        ws.write('H2:H2', _('DATE'), stl1)
        ws.write('I2:I2', _('PAYMENT DATE'), stl1)
        ws.write('J2:J2', _('OPERATION TYPE'), stl1)
        ws.write('K2:K2', _('TRANSFERENCE'), stl1)
        ws.write('L2:L2', _('CURRENCY'), stl1)
        ws.write('M2:M2', _('REQUIRED AMOUNT'), stl1)
        ws.write('N2:N2', _('ACCOUNT'), stl1)
        ws.write('O2:O2', _('RETENTION'), stl1)
        ws.write('P2:P2', _('RETEN ACCOUNT'), stl1)
        ws.write('Q2:Q2', _('DETRACTION'), stl1)
        ws.write('R2:R2', _('VENDOR'), stl1)
        ws.write('S2:S2', _('BANK ACCOUNT'), stl1)
        ws.write('T2:T2', _('DNI/RUC'), stl2)
        ws.write('U2:U2', _('NAME / SOCIAL REASON'), stl2)
        ws.write('V2:V2', _('DOCUMENT TYPE'), stl2)
        ws.write('W2:W2', _('DOCUMENT'), stl2)
        ws.write('X2:X2', _('VENDOR'), stl2)
        ws.write('Y2:Y2', _('RETENTION'), stl2)
        ws.write('Z2:Z2', _('DETRACTION'), stl2)
        ws.write('AA2:AA2', _('AMOUNT'), stl2)
        ws.write('AB2:AB2', _('TOTAL'), stl2)
        ws.write('AC2:AC2', _('RESPONSIBLE'), stl2)
        ws.write('AD2:AD2', _('REFUND EMPLOYEE'), stl2)
        ws.write('AE2:AE2', _('REFUND MKT'), stl2)
        ws.write('AF2:AF2', _('PAYROLL'), stl1)
        ws.write('AG2:AG2', _('STATE(RQ)'), stl1)
        ws.write('AH2:AH2', _('STATE(FL)'), stl1)
        ws.autofilter('A2:AH2')

        records = self._get_query()
        row = 2
        line_aux = False
        for line in records:
            if line_aux != line['requirement']:
                total_lines = line['settlement_lines'] or 0
                ws.write(row, 0, line['requirement'], stl3)
                ws.write(row, 1, line['budget'], stl4)
                ws.write(row, 2, line['cost_center'], stl4)
                ws.write(row, 3, line['ruc'] if line['ruc'] and len(line['ruc']) == 8 else '', stl4)
                ws.write(row, 4, line['ruc'] if line['ruc'] and len(line['ruc']) == 11 else '', stl4)
                ws.write(row, 5, line['provider'], stl3)
                ws.write(row, 6, line['concept'], stl3)
                ws.write(row, 7, line['date_line'] or ' ', stl5)
                ws.write(row, 8, line['payment_date'] or ' ', stl5)
                # ws.write(row, 9, 'TR' if line['refund'] == False else 'RB', stl5)
                ws.write(row, 9, 'TR', stl5)
                ws.write(row, 10, line['operation_number'], stl3)
                ws.write(row, 11, line['currency'], stl4)
                ws.write(row, 12, line['required_amount'], stl6)
                ws.write(row, 13, line['accounting_account'] or '', stl6)
                ws.write(row, 14, line['retention'], stl6)
                # ws.write(row, 15, line['accounting_account'] or '', stl6)
                ws.write(row, 15, '', stl6)
                ws.write(row, 16, line['detraction'], stl6)
                ws.write(row, 17, line['vendor'], stl6)
                # ws.write(row, 18, line['bank_account'] or '', stl7)
                ws.write(row, 18, '', stl7)
                ws.write(row, 19, line['dni_ruc_line'], stl7)
                ws.write(row, 20, line['partner_line'], stl12)
                ws.write(row, 21, line['document_type_line'], stl7)
                ws.write(row, 22, line['document_line'], stl7)
                ws.write(row, 23, line['vendor_line'], stl8)
                ws.write(row, 24, line['retention_line'], stl8)
                ws.write(row, 25, line['detraction_line'], stl8)
                ws.write(row, 26, line['amount_line'], stl8)
                if total_lines == 0:
                    ws.write_formula(row, 27, '=SUM(U%s:U%s)' % ( ( row + 1 ), ( row + 1 ) ), stl8)
                else:
                    ws.write_formula(row, 27, '=SUM(U%s:U%s)' % ( ( row + 1 ), ( row + 1 ) + total_lines - 1 ), stl8)
                ws.write(row, 28, line['responsible'], stl7)
                ws.write(row, 29, '=V%s-J%s' % ( ( row + 1 ), ( row + 1 ) ), stl8)
                ws.write(row, 30, '', stl8)
                ws.write(row, 31, line['payroll_line'], stl4)
                ws.write(row, 32, self.change_state_name(line['requirement_state']), stl4)
                ws.write(row, 33, self.change_state_name(line['settlement_state']), stl4)
                row += 1
            else:
                ws.write(row, 0, line['requirement'], stl9)
                ws.write(row, 1, '', stl9)
                ws.write(row, 2, '', stl9)
                ws.write(row, 3, '', stl9)
                ws.write(row, 4, '', stl9)
                ws.write(row, 5, '', stl9)
                ws.write(row, 6, '', stl9)
                ws.write(row, 7, line['date_line'], stl11)
                ws.write(row, 8, line['payment_date'], stl11)
                ws.write(row, 9, '', stl9)
                ws.write(row, 10, '', stl9)
                ws.write(row, 11, '', stl9)
                ws.write(row, 12, '', stl9)
                ws.write(row, 13, '', stl9)
                ws.write(row, 14, '', stl9)
                ws.write(row, 15, '', stl9)#?
                ws.write(row, 16, '', stl9)
                ws.write(row, 17, '', stl9)
                ws.write(row, 18, '', stl9)
                ws.write(row, 19, line['dni_ruc_line'], stl9)
                ws.write(row, 20, line['partner_line'], stl13)
                ws.write(row, 21, line['document_type_line'], stl9)
                ws.write(row, 22, line['document_line'], stl9)
                ws.write(row, 23, line['vendor_line'], stl10)
                ws.write(row, 24, line['retention_line'], stl10)
                ws.write(row, 25, line['detraction_line'], stl10)
                ws.write(row, 26, line['amount_line'], stl10)
                ws.write(row, 27, '', stl9)
                ws.write(row, 28, line['responsible'], stl9)
                ws.write(row, 29, '', stl9)
                ws.write(row, 30, '', stl9)
                ws.write(row, 31, line['payroll_line'], stl9)
                ws.write(row, 32, self.change_state_name(line['requirement_state']), stl9)
                ws.write(row, 33, self.change_state_name(line['settlement_state']), stl9)
                row += 1
            line_aux = line['requirement']


    def _get_query(self):
        query = """
            SELECT
                dr.name AS requirement,
                b.name AS budget,
                cc.code AS cost_center,
                dr.dni_or_ruc AS ruc,
                rp.name AS provider,
                dr.concept AS concept,
                dr.is_refund as refund,
                dr.accounting_account as accounting_account,
                dr.payment_date AS payment_date,
                dr.operation_number AS operation_number,
                CASE
                    WHEN dr.amount_currency_type = 'soles' THEN 'S/.'
                    WHEN dr.amount_currency_type = 'dolares' THEN '$$'
                END AS currency,
                CASE
                    WHEN dr.amount_soles > 0 THEN dr.amount_soles
                    WHEN dr.amount_uss > 0 then dr.amount_uss
                END AS required_amount,
                dr.retention_amount AS retention,
                dr.detraction_amount AS detraction,
                dr.to_pay_supplier AS vendor,
                s.dni_ruc AS dni_ruc_line,
                s.partner AS partner_line,
                s.date AS date_line,
                --s.account AS account,
                slt.name AS document_type_line,
                s.document AS document_line,
                s.vendor AS vendor_line,
                s.retention AS retention_line,
                s.detraction AS detraction_line,
                -- s.amount AS amount_line,
                s.settle_amount AS amount_line,
                rp2.name AS responsible,
                rpy.name AS payroll_line,
                dr.requirement_state AS requirement_state,
                dr.settlement_state AS settlement_state,
                dr.settlement_total_lines AS settlement_lines
            FROM documental_requirements AS dr
            LEFT JOIN budget AS b ON dr.budget_id=b.id
            LEFT JOIN cost_center AS cc ON b.cost_center_id=cc.id
            LEFT JOIN res_partner AS rp ON rp.id=dr.paid_to
            LEFT JOIN settlement AS s ON dr.id=s.requirement_id
            LEFT JOIN settlement_line_type AS slt ON slt.id=s.document_type_id
            LEFT JOIN res_users AS ru ON ru.id=dr.full_name
            LEFT JOIN res_partner AS rp2 ON rp2.id=ru.partner_id
            LEFT JOIN requirement_payroll AS rpy ON rpy.id=dr.requirement_payroll_id
            WHERE dr.requirement_state IN ('to_settle','settled')
            ORDER BY dr.name DESC
        """
        self._cr.execute(query)
        res_query = self._cr.dictfetchall()
        return res_query
