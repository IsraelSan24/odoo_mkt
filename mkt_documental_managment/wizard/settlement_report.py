from odoo import _, fields, models

class SettlementReport(models.Model):
    _name = 'settlement.report'
    _description = 'Settlement report'
    _inherit = ['report.formats']

    document_type_ids = fields.Many2many(
        'settlement.line.type',
        required=True,
        string='Document type(s)',
        default=lambda self: self.env['settlement.line.type'].search([('short_name', '=', 'RH')]) or False
    )

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
        # Ensure super class has the method before calling it
        if hasattr(super(SettlementReport, self), '_get_file_name'):
            return super(SettlementReport, self)._get_file_name(function_name, file_name=_('Fee Receipt Report'))
        return file_name or _('Fee Receipt Report')


    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Report'))
        style1 = {
            'font_size': 11,
            'bg_color': '#B3356E',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True,
            'bold': 1,
            'border': 1,
            'font_color': 'white',
        }
        style2 = {
            'font_size': 11,
            'align': 'left',
            'valign': 'vcenter',
            'text_wrap': False,
            'border': 1,
        }
        style3 = {
            'font_size': 11,
            'num_format': 'dd/mm/yyyy',
            'border': 1,
            'align': 'center',
        }
        style4 = {
            'font_size': 11,
            'num_format': '#,##0.00',
            'border': 1,
            'align': 'right',
        }
        style5 = {
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': False,
            'border': 1,
        }

        header_format = workbook.add_format(style1)
        cell_format = workbook.add_format(style2)
        date_format = workbook.add_format(style3)
        number_format = workbook.add_format(style4)
        area_format = workbook.add_format(style5)

        ws.set_row(0, 45)

        ws.set_column('A:A', 15)
        ws.set_column('B:B', 10)
        ws.set_column('C:C', 20)
        ws.set_column('D:D', 20)
        ws.set_column('E:E', 15)
        ws.set_column('F:F', 60)
        ws.set_column('G:G', 60)
        ws.set_column('H:H', 15)
        ws.set_column('I:I', 15)
        ws.set_column('J:J', 15)
        ws.set_column('K:K', 15)
        ws.set_column('L:L', 20)
        ws.set_column('M:M', 50)
        ws.set_column('N:N', 20)
        ws.set_column('O:O', 20)
        ws.set_column('P:P', 15)
        ws.set_column('Q:Q', 20)
        ws.set_column('R:R', 15)
        ws.set_column('S:S', 50)
        ws.set_column('T:T', 15)
        ws.set_column('U:U', 20)

        headers = [
            _('Date of Issue'), _('Type of Document Issued'), _('Document'), _('Type of Issuing Doc.'), _('Issuing Doc.'), _('Surnames and Names, Denomination or Company Name of the Issuer'),
            _('Description'), _('Currency of Transaction'), _('Gross Income'), _('Income Tax'), _('Net Income'), _('Area'),
            _('Supervisor'), _('Province'), _('Status Request'), _('RQ Number'), _('Budget'), _('Cost Center'), _('Client'),
            _('Payment Date'), _('Operation Number')
        ]

        for col, header in enumerate(headers):
            ws.write(0, col, header, header_format)

        records = self._get_query()
        for row, line in enumerate(records, 1):
            ws.set_row(row, 20)

            ws.write(row, 0, line.get('date', ''), date_format)
            ws.write(row, 1, line.get('code', ''), cell_format)
            ws.write(row, 2, line.get('document', ''), cell_format)
            ws.write(row, 3, _('RUC'), area_format)
            ws.write(row, 4, line.get('dni_ruc', ''), cell_format)
            ws.write(row, 5, line.get('partner', ''), cell_format)
            ws.write(row, 6, line.get('reason', ''), cell_format)
            ws.write(row, 7, line.get('amount_currency_type', ''), cell_format)
            ws.write(row, 8, line.get('settle_amount', 0.0), number_format)
            ws.write(row, 9, line.get('retention', 0.0), number_format)
            ws.write(row, 10, line.get('vendor', ''), cell_format)
            ws.write(row, 11, _('Contabilidad'), area_format)
            ws.write(row, 12, line.get('requester', ''), cell_format)
            ws.write(row, 13, line.get('province', ''), cell_format)
            ws.write(row, 14, self.change_state_name(line['requirement_state']), cell_format)
            ws.write(row, 15, line.get('rq_number', ''), cell_format)
            ws.write(row, 16, line.get('budget', ''), cell_format)
            ws.write(row, 17, line.get('cost_center', ''), cell_format)
            ws.write(row, 18, line.get('client', ''), cell_format)
            ws.write(row, 19, line.get('payment_date', ''), date_format)
            ws.write(row, 20, line.get('operation_number', ''), cell_format)

        ws.freeze_panes(1, 0)

    def _get_query(self):
        query = """
            SELECT
                s.date,
                dt.short_name as code,
                s.document,
                r.requirement_state as requirement_state,
                s.dni_ruc,
                s.partner,
                s.reason,
                r.amount_currency_type,
                s.settle_amount,
                s.retention,
                s.vendor,
                rp.name as requester,
                st.name as province,
                r.name as rq_number,
                b.name as budget,
                cc.code as cost_center,
                p.name as client,
                r.operation_number,
                r.payment_date
            FROM 
                settlement AS s
                LEFT JOIN settlement_line_type dt ON s.document_type_id = dt.id
                LEFT JOIN documental_requirements r ON s.requirement_id = r.id
                LEFT JOIN res_users ru ON r.full_name = ru.id
                LEFT JOIN res_partner rp ON ru.partner_id = rp.id 
                LEFT JOIN res_country_state st ON rp.state_id = st.id
                LEFT JOIN budget b ON r.budget_id = b.id
                LEFT JOIN cost_center cc ON b.cost_center_id = cc.id
                LEFT JOIN res_partner p ON b.partner_id = p.id
            WHERE
                dt.short_name = 'RH'
            ORDER BY
                s.date DESC
        """

        document_type_ids = tuple(self.document_type_ids.ids)

        if not document_type_ids:
            return []

        placeholders = ', '.join(['%s'] * len(document_type_ids))
        query = query.replace('%s', f"({placeholders})")

        try:
            self._cr.execute(query, document_type_ids)
            return self._cr.dictfetchall()
        except Exception as e:
            return []