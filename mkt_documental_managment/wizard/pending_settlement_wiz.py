from odoo import _, models
import datetime
import io as io
import base64

class PendingSettlement(models.Model):
    _name = 'pending.settlement'
    _description = 'Pending settlement'
    _inherit = ['report.formats']


    def change_state_name(self, state):
        final_state = ''
        if state == 'draft':
            final_state = _('Draft')
        elif state == 'executive':
            final_state = _('V.B Boss')
        elif state == 'responsible':
            final_state = _('V.B Budget Executive')
        elif state == 'intern_control':
            final_state = _('V.B Intern Control')
        elif state == 'administration':
            final_state = _('V.B Administration')
        elif state == 'to_settle':
            final_state = _('To Settle')
        elif state == 'settled':
            final_state = _('Settled')
        else:
            final_state = _('Refused')
        return final_state


    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')


    def _get_file_name(self, function_name, file_name=False):
        dic_name = super(PendingSettlement, self)._get_file_name(function_name, file_name=_('Pending settlements'))
        return dic_name


    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Report'))
        
        ws.set_zoom(75)
        
        style1 = {
            'font_size': 18,
            'bg_color':'#86CBD6',
            'align': 'center',
            'valign': 'vcenter',
            'bold': True,
            'border': 1,
            'text_wrap': True,
        }
        style2 = {
            'font_size': 11,
            'bg_color': '#2474B4',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'text_wrap': True,
        }
        style3 = {
            'font_size': 11,
            'bg_color': '#FAD07A',
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': 'dd/mm/yyyy',
            'text_wrap': True,
        }
        style4 = {
            'font_size': 11,
            'bg_color': '#FAD07A',
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'text_wrap': True,
        }
        
        stl1 = workbook.add_format(style1)
        stl2 = workbook.add_format(style2)
        stl3 = workbook.add_format(style3)
        stl4 = workbook.add_format(style4)

        ws.set_row(3, 37.5)
        ws.set_column('A:A',19)
        ws.set_column('B:B',21.14)
        ws.set_column('C:C',18)
        ws.set_column('D:D',36)
        ws.set_column('E:E',14.43)
        ws.set_column('F:F',17.29)
        ws.set_column('G:G',26)
        ws.set_column('H:H',14.57)
        ws.set_column('I:I',16)
        ws.set_column('J:J',15.57)
        ws.set_column('K:K',20.43)
        ws.set_column('L:L',19)
        ws.set_column('M:M',22.29)

        company = self.env.user.company_id.logo
        if company:
            company_image = io.BytesIO(base64.b64decode(company))
            ws.write(1, 1, '')
            ws.insert_image(1, 1, 'image.png', {
                'image_data': company_image,
                'x_scale': 0.1,
                'y_scale': 0.1,
            })

        ws.merge_range('E2:H2', _('SETTLEMENT PENDINGS'), stl1)
        ws.write('B4:B4', _('PAYMENT DATE'), stl2)
        ws.write('C4:C4', _('REQUIREMENT'), stl2)
        ws.write('D4:D4', _('CONCEPT'), stl2)
        ws.write('E4:E4', _('CURRENCY'), stl2)
        ws.write('F4:F4', _('AMOUNT REQUIRED'), stl2)
        ws.write('G4:G4', _('PAID TO'), stl2)
        ws.write('H4:H4', _('CREDIT CARD'), stl2)
        ws.write('I4:I4', _('BUDGET'), stl2)
        ws.write('J4:J4', _('COST CENTER'), stl2)
        ws.write('K4:K4', _('RESPONSIBLE'), stl2)
        ws.write('L4:L4', _('RQ STATE'), stl2)
        ws.write('M4:M4', _('FL STATE'), stl2)
        ws.autofilter('B4:M4')

        records = self._get_query()
        row = 4
        for line in records:
            ws.write(row, 1, line['payment_date'] if line['payment_date'] else '', stl3)
            ws.write(row, 2, line['requirement'], stl4)
            ws.write(row, 3, line['concept'], stl4)
            ws.write(row, 4, line['currency'], stl4)
            ws.write(row, 5, line['amount'], stl4)
            ws.write(row, 6, line['paid_to'], stl4)
            ws.write(row, 7, 'TC' if line['credit_card'] == True else ' ', stl4)
            ws.write(row, 8, line['budget'], stl4)
            ws.write(row, 9, line['cost_center'], stl4)
            ws.write(row, 10, line['responsible'], stl4)
            ws.write(row, 11, self.change_state_name(line['requirement_state']), stl4)
            ws.write(row, 12, self.change_state_name(line['settlement_state']), stl4)
            row += 1


    def _get_query(self):
        query = """
            SELECT
                COALESCE(dr.payment_date, rp.payment_date) AS payment_date,
                dr.name AS requirement,
                dr.concept AS concept,
                CASE
                    WHEN dr.amount_currency_type = 'soles' THEN 'S/'
                    WHEN dr.amount_currency_type = 'dolares' THEN '$$'
                END AS currency,
                CASE
                    WHEN dr.amount_soles > 0 THEN dr.amount_soles
                    WHEN dr.amount_uss > 0 THEN dr.amount_uss
                END AS amount,
                rp2.name AS paid_to,
                dr.card_payment AS credit_card,
                b.name AS budget,
                cc.code AS cost_center,
                rp3.name AS responsible,
                dr.requirement_state AS requirement_state,
                dr.settlement_state AS settlement_state
            FROM documental_requirements AS dr
            LEFT JOIN res_partner AS rp2 ON rp2.id = dr.paid_to
            LEFT JOIN budget AS b ON b.id = dr.budget_id
            LEFT JOIN cost_center AS cc ON cc.id = b.cost_center_id
            LEFT JOIN res_users AS ru ON ru.id = dr.full_name
            LEFT JOIN res_partner AS rp3 ON rp3.id = ru.partner_id
            LEFT JOIN (
                SELECT requirement_id, MIN(payment_date) AS payment_date 
                FROM requirement_payment 
                GROUP BY requirement_id
            ) rp ON rp.requirement_id = dr.id
            WHERE 
                (dr.payment_date IS NOT NULL OR rp.payment_date IS NOT NULL)
                AND dr.settlement_state IN ('draft', 'external_control', 'executive', 'responsible', 'intern_control', 'refused')
                AND dr.active = TRUE
            ORDER BY dr.name DESC;
        """
        self._cr.execute(query)
        res_query = self._cr.dictfetchall()
        return res_query
