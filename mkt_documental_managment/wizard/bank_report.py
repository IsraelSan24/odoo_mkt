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
            final_state = _('To Settle')
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
        ws = workbook.add_worksheet(_('Report'))

        ws.set_zoom(70)
        ws.set_column('A:A', 20)
        ws.set_column('B:B', 17)
        ws.set_column('C:C', 13.71)
        ws.set_column('D:D', 19.57)
        ws.set_column('E:E', 19.57)
        ws.set_column('F:F', 37.57)
        ws.set_column('G:G', 45.29)
        ws.set_column('H:H', 19.57)
        ws.set_column('I:I', 19.14)
        ws.set_column('J:J', 10.86)
        ws.set_column('K:K', 20.43)
        ws.set_column('L:L', 10.86)
        ws.set_column('M:M', 23.29)
        ws.set_column('N:N', 16)
        ws.set_column('O:O', 13.43)
        ws.set_column('P:P', 20)
        ws.set_column('Q:Q', 14.86)
        ws.set_column('R:R', 33)
        ws.set_column('S:S', 19)
        ws.set_column('T:T', 15.43)
        ws.set_column('U:U', 16.29)
        ws.set_column('V:V', 18.14)
        ws.set_column('W:W', 16.43)
        ws.set_column('X:X', 18)
        ws.set_column('Y:Y', 13.86)
        ws.set_column('Z:Z', 21.29)
        ws.set_column('AA:AA', 52.29)
        ws.set_column('AB:AB', 16.43)
        ws.set_column('AC:AC', 24.86)
        ws.set_column('AD:AD', 16)
        ws.set_column('AE:AE', 20)
        ws.set_column('AF:AF', 22.43)
        ws.set_column('AG:AG', 18.71)
        ws.set_column('AH:AH', 18.86)
        ws.freeze_panes(2, 1)

        style1 = {
            'font_color':'#000000',
            'bg_color':'#FFFFFF',
            'align':'center',
            'border':2,
            'bold':True
        }
        style2 = {
            'font_color':'#FFFFFF',
            'bg_color':'#000000',
            'align':'center',
            'border':2,
            'bold':True
        }
        style3 = {
            'font_color':'#000000',
            'bg_color':'#8A8A8A',
            'align':'center',
            'border':1,
            'bold':True
        }
        style4 = {
            'font_color':'#000000',
            'bg_color':'#8A8A8A',
            'align':'center',
            'border':1,
            'bold':True,
            'num_format':'dd/mm/yy',
        }
        style5 = {
            'font_color':'#000000',
            'bg_color':'#A2A2A2',
            'align':'center',
            'border':1,
            'bold':True,
            'num_format':'#,##0.00',
        }
        style6 = {
            'font_color':'#000000',
            'bg_color':'#FFFFFF',
            'align':'center',
            'border':1,
            'bold':True,
            'num_format':'#,##0.00',
        }
        style7 = {
            'font_color':'#000000',
            'bg_color':'#FFFFFF',
            'border':1,
            'bold':True,
            'align': 'center',
        }

        stl1 = workbook.add_format(style1)
        stl2 = workbook.add_format(style2)
        stl3 = workbook.add_format(style3)
        stl4 = workbook.add_format(style4)
        stl5 = workbook.add_format(style5)
        stl6 = workbook.add_format(style6)
        stl7 = workbook.add_format(style7)

        ws.write('A2:A2', _('RQ N°'), stl1)
        ws.write('B2:B2', _('BUDGET N°'), stl1)
        ws.write('C2:C2', _('DNI'), stl1)
        ws.write('D2:D2', _('RUC'), stl1)
        ws.write('E2:E2', _('CC N°'), stl1)
        ws.write('F2:F2', _('PROVIDER'), stl1)
        ws.write('G2:G2', _('CONCEPT'), stl1)
        ws.write('H2:H2', _('PAYMENT DATE'), stl1)
        ws.write('I2:I2', _('OPERATION TYPE'), stl1)
        ws.write('J2:J2', _('TRANFER N°'), stl1)
        ws.write('K2:K2', _('CURRENCY'), stl1)
        ws.write('L2:L2', _('REQUIRED AMOUNT'), stl1)
        ws.write('M2:M2', _('ACCOUNT'), stl1)
        ws.write('N2:N2', _('RETENTION'), stl1)
        ws.write('O2:O2', _('DETRACTION'), stl1)
        ws.write('P2:P2', _('VENDOR'), stl1)
        ws.write('Q2:Q2', _('BANK ACCOUNT'), stl1)
        ws.write('R2:R2', _('DATE'), stl1)
        ws.write('S2:S2', _('DNI/RUC'), stl2)
        ws.write('T2:T2', _('NAME / SOCIAL REASON'), stl2)
        ws.write('U2:U2', _('DOCUMENT TYPE'), stl2)
        ws.write('V2:V2', _('DOCUMENT'), stl2)
        ws.write('W2:W2', _('VENDOR'), stl2)
        ws.write('X2:X2', _('RETENTION'), stl2)
        ws.write('Y2:Y2', _('DETRACTION'), stl2)
        ws.write('Z2:Z2', _('AMOUNT'), stl2)
        ws.write('AA2:AA2', _('TOTAL'), stl2)
        ws.write('AB2:AB2', _('RESPONSIBLE'), stl2)
        ws.write('AC2:AC2', _('REFUND EMPLOYEE'), stl2)
        ws.write('AD2:AD2', _('REFUND MKT'), stl2)
        ws.write('AE2:AE2', _('PAYROLL'), stl1)
        ws.write('AF2:AF2', _('STATE(RQ)'), stl1)
        ws.write('AG2:AG2', _('STATE(FL)'), stl1)
        ws.autofilter('AH2:AH2')

        records = self._get_query()
        row = 2
        line_aux = False
        for line in records:
            if line_aux != line['requirement']:
                total_lines = line['settlement_lines'] or 0
                ws.write(row, 0, line['requirement'], stl3)
                ws.write(row, 1, line['budget'], stl3)
                ws.write(row, 2, line['ruc'] if line['ruc'] and len(line['ruc']) == 8 else '', stl3)
                ws.write(row, 3, line['ruc'] if line['ruc'] and len(line['ruc']) == 11 else '', stl3)
                ws.write(row, 4, line['cost_center'], stl3)
                ws.write(row, 5, line['supplier'], stl3)
                ws.write(row, 6, (line['concept'] or '').upper(), stl3)
                ws.write(row, 7, line['payment_date'], stl4)
                ws.write(row, 8, 'TR', stl4)
                ws.write(row, 9, line['operation_number'], stl3)
                ws.write(row, 10, line['currency'], stl3)
                ws.write(row, 11, line['amount'], stl3)
                ws.write(row, 12, line['accounting_account'] or '', stl3)
                ws.write(row, 13, line['retention'], stl3)
                ws.write(row, 14, line['detraction'], stl3)
                ws.write(row, 15, line['vendor'], stl3)
                ws.write(row, 16, '', stl3)
                ws.write(row, 17, line['date_line'] or ' ', stl4)
                ws.write(row, 18, line['dni_ruc_line'], stl5)
                ws.write(row, 19, line['partner_line'], stl5)
                ws.write(row, 20, line['document_type'], stl5)
                ws.write(row, 21, line['document'], stl5)
                ws.write(row, 22, line['settlement_vendor'], stl5)
                ws.write(row, 23, line['settlement_retention'], stl5)
                ws.write(row, 24, line['settlement_detraction'], stl5)
                ws.write(row, 25, line['settlement_amount'], stl5)
                if total_lines == 0:
                    ws.write_formula(row, 26, '=SUM(R%s:R%s)' % ( ( row + 1 ), ( row + 1 ) ), stl5)
                else:
                    ws.write_formula(row, 26, '=SUM(R%s:R%s)' % ( ( row + 1 ), ( row + 1 ) + total_lines - 1 ), stl5)
                ws.write(row, 27, line['responsible'], stl5)
                ws.write(row, 28, '=S%s-I%s' % ( ( row + 1 ), ( row + 1 ) ), stl5)
                ws.write(row, 29, '', stl5)
                ws.write(row, 30, line['payroll'], stl5)
                ws.write(row, 31, self.change_state_name(line['requirement_state']), stl3)
                ws.write(row, 32, self.change_state_name(line['settlement_state']), stl3)
                row += 1
            else:
                ws.write(row, 0, '', stl7)
                ws.write(row, 1, '', stl7)
                ws.write(row, 2, '', stl7)
                ws.write(row, 3, '', stl7)
                ws.write(row, 4, '', stl7)
                ws.write(row, 5, '', stl7)
                ws.write(row, 6, '', stl7)
                ws.write(row, 7, '', stl7)
                ws.write(row, 8, '', stl7)
                ws.write(row, 9, '', stl7)
                ws.write(row, 10, '', stl7)
                ws.write(row, 11, '', stl7)
                ws.write(row, 12, '', stl7)
                ws.write(row, 13, '', stl7)
                ws.write(row, 14, '', stl7)
                ws.write(row, 15, '', stl7)
                ws.write(row, 16, '', stl7)
                ws.write(row, 17, line['date_line'], stl7)
                ws.write(row, 18, line['dni_ruc_line'], stl7)
                ws.write(row, 19, line['partner_line'], stl7)
                ws.write(row, 20, line['document_type'], stl7)
                ws.write(row, 21, line['document'], stl7)
                ws.write(row, 22, line['settlement_vendor'], stl6)
                ws.write(row, 23, line['settlement_retention'], stl6)
                ws.write(row, 24, line['settlement_detraction'], stl6)
                ws.write(row, 25, line['settlement_amount'], stl6)
                ws.write(row, 26, ' ', stl6)
                ws.write(row, 27, line['responsible'], stl7)
                ws.write(row, 28, ' ', stl6)
                ws.write(row, 29, '', stl6)
                ws.write(row, 30, line['payroll'], stl6)
                ws.write(row, 31, self.change_state_name(line['requirement_state']), stl3)
                ws.write(row, 32, self.change_state_name(line['requirement_state']), stl3)
                row += 1
            line_aux = line['requirement']


    def _get_query(self):
        query = """
            SELECT
                dr.name AS requirement,
                b.name AS budget,
                cc.code AS cost_center,
                dr.dni_or_ruc AS ruc,
                dr.accounting_account as accounting_account,
                s.date AS date_line,
                rp.name AS supplier,
                dr.concept AS concept,
                dr.payment_date AS payment_date,
                COALESCE(dr.operation_number, dr.check_number) AS operation_number,
                CASE
                    WHEN dr.amount_currency_type = 'soles' THEN 'S/'
                    WHEN dr.amount_currency_type = 'dolares' THEN '$$'
                END AS currency,
                CASE
                    WHEN dr.amount_currency_type = 'soles' THEN dr.amount_soles
                    WHEN dr.amount_currency_type = 'dolares' THEN dr.amount_uss
                END AS amount,
                dr.total_retention AS retention,
                dr.total_detraction AS detraction,
                dr.total_vendor AS vendor,
                s.document AS document,
                slt.name AS document_type,
                s.vendor AS settlement_vendor,
                s.retention AS settlement_retention,
                s.detraction AS settlement_detraction,
                -- s.amount AS settlement_amount,
                s.settle_amount AS settlement_amount,
                s.dni_ruc AS dni_ruc_line,
                s.partner AS partner_line,
                rp2.name AS responsible,
                rpy.code AS payroll,
                dr.settlement_administration_signed_on AS settlement_date,
                dr.requirement_state AS requirement_state,
                dr.settlement_state AS settlement_state,
                dr.settlement_total_lines AS settlement_lines
            FROM documental_requirements AS dr
            LEFT JOIN budget AS b ON b.id=dr.budget_id
            LEFT JOIN cost_center AS cc ON cc.id=b.cost_center_id
            LEFT JOIN res_partner AS rp ON rp.id=dr.paid_to
            LEFT JOIN settlement AS s ON dr.id=s.requirement_id
            LEFT JOIN settlement_line_type AS slt ON slt.id=s.document_type_id
            LEFT JOIN res_users AS ru ON ru.id=dr.full_name
            LEFT JOIN res_partner AS rp2 ON rp2.id=ru.partner_id
            LEFT JOIN requirement_payroll AS rpy ON rpy.id=dr.requirement_payroll_id
            WHERE dr.payment_date IS NOT NULL
            ORDER BY dr.name DESC
        """
        self._cr.execute(query)
        res_query = self._cr.dictfetchall()
        return res_query
