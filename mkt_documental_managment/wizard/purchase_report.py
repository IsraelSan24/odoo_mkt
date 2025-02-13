from odoo import _, fields, models, api
from odoo.exceptions import ValidationError

class AccountPurchaseReport(models.Model):
    _name = 'account.purchase.report'
    _description = 'Account purchase report'
    _inherit = ['report.formats']

    document_type_ids = fields.Many2many('settlement.line.type', required=True, string='Document type(s)')
    month_ids = fields.Many2many('months', required=True, string='Voucher month')
    year_ids = fields.Many2many(comodel_name='years', string="Year", required=True)


    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')


    def _get_file_name(self, function_name, file_name=False):
        dic_name = super(AccountPurchaseReport, self)._get_file_name(function_name, file_name=_('Purchase report'))
        return dic_name


    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Report'))

        style1 = {
            'font_size':11,
            'bg_color':'#FFFF00',
            'align':'center',
            'valign':'vcenter',
            'text_wrap':True,
            'bold':1,
            'border':1,
        }
        style2 = {
            'font_size':11,
            'bg_color':'#FFC000',
            'align':'center',
            'valign':'vcenter',
            'text_wrap':True,
            'border':1,
        }
        style3 = {
            'font_size':11,
            'align':'left',
            'valign':'top',
            'text_wrap':True,
            'border':1,
        }
        style4 = {
            'font_size':11,
            'num_format':'dd/mm/yyyy',
        }
        
        stl1 = workbook.add_format(style1)
        stl2 = workbook.add_format(style2)
        stl3 = workbook.add_format(style3)
        stl4 = workbook.add_format(style4)
        
        ws.set_row(0, 45)
        ws.set_row(1, 135)
        
        ws.set_column('A:A', 16)
        ws.set_column('B:B', 12)
        ws.set_column('C:C', 18)
        ws.set_column('D:D', 13)
        ws.set_column('E:E', 11)
        ws.set_column('F:F', 40.29)
        ws.set_column('G:G', 18)
        ws.set_column('H:H', 18)
        ws.set_column('I:I', 16)
        ws.set_column('J:J', 14)
        ws.set_column('K:K', 15)
        ws.set_column('L:L', 15)
        ws.set_column('M:M', 16)
        ws.set_column('N:N', 12)
        ws.set_column('O:O', 18)
        ws.set_column('P:P', 18)
        ws.set_column('Q:Q', 18)
        ws.set_column('R:R', 17)
        ws.set_column('S:S', 20.43)
        ws.set_column('T:T', 16)
        ws.set_column('U:U', 16)
        ws.set_column('V:V', 15)
        ws.set_column('W1:W1', 32.43)
        ws.set_column('X1:X1', 15)
        ws.set_column('Y1:Y1', 18)
        ws.set_column('Z1:Z1', 14)
        ws.set_column('AA:AA', 20.43)
        ws.set_column('AB:AB', 14)
        ws.set_column('AC:AC', 15)
        ws.set_column('AD:AD', 15)
        ws.set_column('AE:AE', 15)
        ws.set_column('AF:AF', 19)
        ws.set_column('AG:AG', 19)
        ws.set_column('AH:AH', 19)
        ws.set_column('AI:AI', 17)
        ws.set_column('AJ:AJ', 22)
        ws.set_column('AK:AK', 22)
        ws.set_column('AL:AL', 22)
        ws.set_column('AM:AM', 18)
        ws.set_column('AN:AN', 18)
        ws.set_column('AO:AO', 18)
        
        ws.write('A1:A1', _('Field'), stl1)
        ws.write('B1:B1', _('Sub Diary'), stl2)
        ws.write('C1:C1', _('Voucher Number'), stl2)
        ws.write('D1:D1', _('Voucher Date'), stl2)
        ws.write('E1:E1', _('Currency Code'), stl2)
        ws.write('F1:F1', _('Main Gloss'), stl2)
        ws.write('G1:G1', _('Change type'), stl2)
        ws.write('H1:H1', _('Conversion type'), stl2)
        ws.write('I1:I1', _('Currency conversion flag'), stl2)
        ws.write('J1:J1', _('Change type date'), stl2)
        ws.write('K1:K1', _('Account Accountant'), stl2)
        ws.write('L1:L1', _('Annex Code'), stl2)
        ws.write('M1:M1', _('Cost Center Code'), stl2)
        ws.write('N1:N1', _('Credit/Debit'), stl2)
        ws.write('O1:O1', _('Original Amount'), stl2)
        ws.write('P1:P1', _('Dollar Amount'), stl2)
        ws.write('Q1:Q1', _('Soles Amount'), stl2)
        ws.write('R1:R1', _('Document Type'), stl2)
        ws.write('S1:S1', _('Document Number'), stl2)
        ws.write('T1:T1', _('Document Date'), stl2)
        ws.write('U1:U1', _('Due Date'), stl2)
        ws.write('V1:V1', _('Area Code'), stl2)
        ws.write('W1:W1', _('Detail Gloss'), stl2)
        ws.write('X1:X1', _('Auxiliar Annex Code'), stl2)
        ws.write('Y1:Y1', _('Payment Method'), stl2)
        ws.write('Z1:Z1', _('Reference Document Type'), stl2)
        ws.write('AA1:AA1', _('Reference Document Number'), stl2)
        ws.write('AB1:AB1', _('Reference Document Date'), stl2)
        ws.write('AC1:AC1', _('Machine Register N°. Reference Document Type'), stl2)
        ws.write('AD1:AD1', _('Taxable Base Document Reference'), stl2)
        ws.write('AE1:AE1', _('IGV Document Provision'), stl2)
        ws.write('AF1:AF1', _('Reference Type in state MQ'), stl2)
        ws.write('AG1:AG1', _('Register Box Serie Number'), stl2)
        ws.write('AH1:AH1', _('Operation Date'), stl2)
        ws.write('AI1:AI1', _('Rate type'), stl2)
        ws.write('AJ1:AJ1', _('Detraction/Perception Rate'), stl2)
        ws.write('AK1:AK1', _('Taxable Base Detraction/Perception Dollar'), stl2)
        ws.write('AL1:AL1', _('Taxable Base Detraction/Perception Soles'), stl2)
        ws.write('AM1:AM1', _("Change Type for 'F'"), stl2)
        ws.write('AN1:AN1', _('IGV Amount without tax creditt right'), stl2)
        ws.write('AO1:AO1', _('IGV Rate'), stl2)

        ws.write('A2:A2', _('Restrictions'), stl1)
        ws.write('B2:B2', _('Ver T.G. 02'), stl3)
        ws.write('C2:C2', _('Los dos primeros dígitos son el mes y los otros 4 siguientes un correlativo'), stl3)
        ws.write('D2:D2', _(' '), stl3)
        ws.write('E2:E2', _('Ver T.G. 03'), stl3)
        ws.write('F2:F2', _(' '), stl3)
        ws.write('G2:G2', _("Llenar  solo si Tipo de Conversión es 'C'. Debe estar entre >=0 y <=9999.999999"), stl3)
        ws.write('H2:H2', _("Solo: 'C'= Especial, 'M'=Compra, 'V'=Venta , 'F' De acuerdo a fecha"), stl3)
        ws.write('I2:I2', _("Solo: 'S' = Si se convierte, 'N'= No se convierte"), stl3)
        ws.write('J2:J2', _("Si  Tipo de Conversión 'F'"), stl3)
        ws.write('K2:K2', _('Debe existir en el Plan de Cuentas'), stl3)
        ws.write('L2:L2', _('Si Cuenta Contable tiene seleccionado Tipo de Anexo, debe existir en la tabla de Anexos'), stl3)
        ws.write('M2:M2', _('Si Cuenta Contable tiene habilitado C. Costo, Ver T.G. 05'), stl3)
        ws.write('N2:N2', _("'D' ó 'H'"), stl3)
        ws.write('O2:O2', _("Importe original de la cuenta contable. Obligatorio, debe estar entre >=0 y <=99999999999.99"), stl3)
        ws.write('P2:P2', _("Importe de la Cuenta Contable en Dólares. Obligatorio si Flag de Conversión de Moneda esta en 'N', debe estar entre >=0 y <=99999999999.99"), stl3)
        ws.write('Q2:Q2', _("Importe de la Cuenta Contable en Soles. Obligatorio si Flag de Conversión de Moneda esta en 'N', debe estra entre >=0 y <=99999999999.99"), stl3)
        ws.write('R2:R2', _('Si Cuenta Contable tiene habilitado el Documento Referencia Ver T.G. 06'), stl3)
        ws.write('S2:S2', _('Si Cuenta Contable tiene habilitado el Documento Referencia Incluye Serie y Número'), stl3)
        ws.write('T2:T2', _('Si Cuenta Contable tiene habilitado el Documento Referencia'), stl3)
        ws.write('U2:U2', _('Si Cuenta Contable tiene habilitada la Fecha de Vencimiento'), stl3)
        ws.write('V2:V2', _('Si Cuenta Contable tiene habilitada el Area. Ver T.G. 26'), stl3)
        ws.write('W2:W2', _(' '), stl3)
        ws.write('X2:X2', _('Si Cuenta Contable tiene seleccionado Tipo de Anexo Referencia'), stl3)
        ws.write('Y2:Y2', _("Si Cuenta Contable tiene habilitado Tipo Medio Pago. Ver T.G. 'S1'"), stl3)
        ws.write('Z2:Z2', _("Si Tipo de Documento es 'NA' ó 'ND' Ver T.G. 06"), stl3)
        ws.write('AA2:AA2', _("Si Tipo de Documento es 'NC', 'NA' ó 'ND', incluye Serie y Número"), stl3)
        ws.write('AB2:AB2', _("Si Tipo de Documento es 'NC', 'NA' ó 'ND'"), stl3)
        ws.write('AC2:AC2', _("Si Tipo de Documento es 'NC', 'NA' ó 'ND'. Solo cuando el Tipo Documento de Referencia 'TK'"), stl3)
        ws.write('AD2:AD2', _("Si Tipo de Documento es 'NC', 'NA' ó 'ND'"), stl3)
        ws.write('AE2:AE2', _("Si Tipo de Documento es 'NC', 'NA' ó 'ND'"), stl3)
        ws.write('AF2:AF2', _("Si la Cuenta Contable tiene Habilitado Documento Referencia 2 y  Tipo de Documento es 'TK'"), stl3)
        ws.write('AG2:AG2', _("Si la Cuenta Contable teien Habilitado Documento Referencia 2 y  Tipo de Documento es 'TK'"), stl3)
        ws.write('AH2:AH2', _("Si la Cuenta Contable tiene Habilitado Documento Referencia 2. Cuando Tipo de Documento es 'TK', consignar la fecha de emision del ticket"), stl3)
        ws.write('AI2:AI2', _("Si la Cuenta Contable tiene configurada la Tasa:  Si es '1' ver T.G. 28 y '2' ver T.G. 29"), stl3)
        ws.write('AJ2:AJ2', _("Si la Cuenta Contable tiene conf. en Tasa:  Si es '1' ver T.G. 28 y '2' ver T.G. 29. Debe estar entre >=0 y <=999.99"), stl3)
        ws.write('AK2:AK2', _("Si la Cuenta Contable tiene configurada la Tasa. Debe ser el importe total del documento y estar entre >=0 y <=99999999999.99"), stl3)
        ws.write('AL2:AL2', _("Si la Cuenta Contable tiene configurada la Tasa. Debe ser el importe total del documento y estar entre >=0 y <=99999999999.99"), stl3)
        ws.write('AM2:AM2', _("Especificar solo si Tipo Conversión es 'F'. Se permite 'M' Compra y 'V' Venta."), stl3)
        ws.write('AN2:AN2', _("Especificar solo para comprobantes de compras con IGV sin derecho de crédito Fiscal. Se detalle solo en la cuenta 42xxxx"), stl3)
        ws.write('AO2:AO2', _('Obligatorio para comprobantes de compras, valores validos 0,10,18.'), stl3)

        ws.write('A3:A3', _('Tamaño/Formato'), stl1)
        ws.write('B3:B3', _('4 Caracteres'), stl3)
        ws.write('C3:C3', _('6 Caracteres'), stl3)
        ws.write('D3:D3', _('dd/mm/aaaa'), stl3)
        ws.write('E3:E3', _('2 Caracteres'), stl3)
        ws.write('F3:F3', _('40 Caracteres'), stl3)
        ws.write('G3:G3', _('Numérico 11, 6'), stl3)
        ws.write('H3:H3', _('1 Caracteres'), stl3)
        ws.write('I3:I3', _('1 Caracteres'), stl3)
        ws.write('J3:J3', _('dd/mm/aaaa'), stl3)
        ws.write('K3:K3', _('12 Caracteres'), stl3)
        ws.write('L3:L3', _('18 Caracteres'), stl3)
        ws.write('M3:M3', _('6 Caracteres'), stl3)
        ws.write('N3:N3', _('1 Carácter'), stl3)
        ws.write('O3:O3', _('Numérico 14,2'), stl3)
        ws.write('P3:P3', _('Numérico 14,2'), stl3)
        ws.write('Q3:Q3', _('Numérico 14,2'), stl3)
        ws.write('R3:R3', _('2 Caracteres'), stl3)
        ws.write('S3:S3', _('20 Caracteres'), stl3)
        ws.write('T3:T3', _('dd/mm/aaaa'), stl3)
        ws.write('U3:U3', _('dd/mm/aaaa'), stl3)
        ws.write('V3:V3', _('3 Caracteres'), stl3)
        ws.write('W3:W3', _('30 Caracteres'), stl3)
        ws.write('X3:X3', _('18 Caracteres'), stl3)
        ws.write('Y3:Y3', _('8 Caracteres'), stl3)
        ws.write('Z3:Z3', _('2 Caracteres'), stl3)
        ws.write('AA3:AA3', _('20 Caracteres'), stl3)
        ws.write('AB3:AB3', _('dd/mm/aaaa'), stl3)
        ws.write('AC3:AC3', _('20 Caracteres'), stl3)
        ws.write('AD3:AD3', _('Numérico 14,2'), stl3)
        ws.write('AE3:AE3', _('Numérico 14,2'), stl3)
        ws.write('AF3:AF3', _("'MQ'"), stl3)
        ws.write('AG3:AG3', _('15 caracteres'), stl3)
        ws.write('AH3:AH3', _('dd/mm/aaaa'), stl3)
        ws.write('AI3:AI3', _('5 Caracteres'), stl3)
        ws.write('AJ3:AJ3', _('Numérico 14,2'), stl3)
        ws.write('AK3:AK3', _('Numérico 14,2'), stl3)
        ws.write('AL3:AL3', _('Numérico 14,2'), stl3)
        ws.write('AM3:AM3', _('1 Caracter'), stl3)
        ws.write('AN3:AN3', _('Numérico 14,2'), stl3)
        ws.write('AO3:AO3', _('Numérico 14,2'), stl3)
        ws.autofilter('A3:AO3')

        records = self._get_query()
        row = 3
        for line in records:
            ws.write(row, 0, ' ')
            ws.write(row, 1, line['subdiary'])
            ws.write(row, 2, line['voucher_number'])
            ws.write(row, 3, line['voucher_date'], stl4)
            ws.write(row, 4, line['currency_code'])
            ws.write(row, 5, line['main_gloss'])
            ws.write(row, 6, line['change_type'])
            ws.write(row, 7, line['conversion_type'])
            ws.write(row, 8, line['flag_currency_conversion'])
            ws.write(row, 9, line['exchange_type_date'], stl4)
            ws.write(row, 10, line['account_code'])
            ws.write(row, 11, line['annex_code'])
            if line['cost_center_code'] in ('1991','2081','2091','2101'):
                ws.write(row, 12, '1991')
            else:
                ws.write(row, 12, line['cost_center_code'])
            if line['debit'] and line['debit'] > 0:    
                ws.write(row, 13, 'D')
            if line['credit'] and line['credit'] > 0:    
                ws.write(row, 13, 'H')
            ws.write(row, 14, line['credit_debit'])
            ws.write(row, 15, '')
            ws.write(row, 16, '')
            ws.write(row, 17, 'DR' if line['account_code'] == '421203' else line['document_code'])
            ws.write(row, 18, line['document_number'])
            if line['account_code'] == '421203':
                if line['detraction_date']:
                    ws.write(row, 19, line['detraction_date'], stl4)
                else:
                    ws.write(row, 19, line['document_date'], stl4)
            else:
                ws.write(row, 19, line['document_date'], stl4)
            # ws.write(row, 19, line['document_date'], stl4)
            ws.write(row, 20, line['due_date'], stl4)
            ws.write(row, 21, '')
            ws.write(row, 22, line['detail_gloss'])
            ws.write(row, 23, line['auxiliar_annex_code'])
            ws.write(row, 24, '')
            ws.write(row, 25, line['reference_document_type'])
            ws.write(row, 26, line['reference_document_number'])
            ws.write(row, 27, line['reference_document_date'], stl4)
            ws.write(row, 28, '')
            ws.write(row, 29, '')
            ws.write(row, 30, '')
            ws.write(row, 31, '')
            ws.write(row, 32, '')
            ws.write(row, 33, '')
            ws.write(row, 34, line['rate_type'])
            ws.write(row, 35, line['detraction_retention_type'])
            ws.write(row, 36, '')
            ws.write(row, 37, line['soles_detraction_retention_amount'])
            ws.write(row, 38, '')
            ws.write(row, 39, '')
            ws.write(row, 40, line['tax_percentage'])
            row += 1


    def _get_query(self):
        query = """
            SELECT
                s.subdiary AS subdiary,
                s.voucher_number AS voucher_number,
                s.voucher_date AS voucher_date,
                CASE
                    WHEN s.currency = 'soles' THEN 'MN'
                    WHEN s.currency = 'dolares' THEN 'US'
                    ELSE ' '
                END AS currency_code,
                s.change_type AS change_type,
                s.main_gloss AS main_gloss,
                s.conversion_type AS conversion_type,
                s.flag_currency_conversion AS flag_currency_conversion,
                s.exchange_type_date AS exchange_type_date,
                aa.code AS account_code,
                sj.annex_code AS annex_code,
                cc.code AS cost_center_code,
                sj.debit AS debit,
                sj.credit AS credit,
                CASE
                    WHEN sj.credit > 0 THEN sj.credit
                    ELSE sj.debit
                END AS credit_debit,
                slt.short_name AS document_code,
                s.due_date AS due_date,
                s.detail_gloss AS detail_gloss,
                s.date AS document_date,
                s.detraction_date AS detraction_date,
                sj.auxiliar_annex_code AS auxiliar_annex_code,
                sj.reference_document_type AS reference_document_type,
                sj.reference_document_date AS reference_document_date,
                sj.reference_document_number AS reference_document_number,
                sj.document_number AS document_number,
                sj.soles_detraction_retention_amount AS soles_detraction_retention_amount,
                sj.rate_type AS rate_type,
                sj.detraction_retention_type AS detraction_retention_type,
                tt.percentage AS tax_percentage
            FROM settlement AS s
                LEFT JOIN settlement_journal AS sj ON sj.settlement_id=s.id
                LEFT JOIN documental_requirements AS dr ON dr.id=s.requirement_id
                LEFT JOIN account_account AS aa ON aa.id=sj.account_id
                LEFT JOIN cost_center AS cc ON cc.id=sj.cost_center_id
                LEFT JOIN settlement_line_type AS slt ON slt.id=s.document_type_id
                LEFT JOIN tax_taxes AS tt ON tt.id=s.tax_id
            WHERE dr.settlement_state IN ('executive','responsible','intern_control','administration','to_settle','settled','refused') AND s.document_type_id IN %s AND LPAD(EXTRACT(MONTH FROM s.voucher_date)::text, 2, '0') IN %s AND EXTRACT(YEAR FROM s.voucher_date)::text IN %s
            ORDER BY requirement_id DESC
        """
        document_type_ids = tuple(self.document_type_ids.ids)
        selected_months = tuple(self.month_ids.mapped('number')) if self.month_ids else ()
        selected_years = tuple(self.year_ids.mapped('name')) if self.year_ids else ()
        if len(document_type_ids) == 1:
            document_type_ids = ( document_type_ids[0], )

        self._cr.execute(query, (document_type_ids,selected_months,selected_years))
        res_query = self._cr.dictfetchall()
        return res_query
