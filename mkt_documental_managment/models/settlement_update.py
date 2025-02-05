from odoo import _, api, fields, models
import pandas as pd
import base64
import io
import logging
_logger = logging.getLogger(__name__)

update_types = [
    ('subdiary','Subdiary'),
    ('detractions','Detractions'),
]

class SettlementUpdate(models.Model):
    _name = 'settlement.update'
    _description = 'Settlement update'
    _order = 'id desc'

    name = fields.Char(string='Name')
    file_document = fields.Binary(string='File document')
    document_filename = fields.Char(compute='_compute_filename_document', string='Document filename')
    update_type = fields.Selection(selection=update_types, default='subdiary', string='Updates types')
    year_month_id = fields.Many2one(comodel_name='year.month', string='Update Year/Month')
    state = fields.Selection(selection=[('draft','Draft'),('done','Done')], default='draft', string='State')


    @api.depends('file_document','year_month_id','update_type')
    def _compute_filename_document(self):
        for rec in self:
            if rec.file_document and rec.year_month_id:
                if rec.update_type == 'subdiary':
                    rec.document_filename = 'updt' + rec.year_month_id.name
                else:
                    rec.document_filename = rec.year_month_id.name + '°DR'
            else:
                rec.document_filename = False


    def update_subdiary_from_xlsx(self):
        if not self.file_document:
            raise ValueError(_('There is no subdiario file.'))
        decoded_file = base64.b64decode(self.file_document)
        excel_file = io.BytesIO(decoded_file)
        df = pd.read_excel(excel_file)
        for index, row in df.iterrows():
            ruc = row['DNI/RUC']
            document = row['DOCUMENTO']
            subdiary = row['SUBDIARIO']
            voucher_number = row['COMPROBANTE']
            voucher_date = row['FECHA_COMPROBANTE']
            if pd.isna(voucher_date):
                voucher_date = False
            else:
                voucher_date = voucher_date.date() if isinstance(voucher_date, pd.Timestamp) else voucher_date
            settlements = self.env['settlement'].search([
                ('dni_ruc','=',ruc),
                ('document','=',document),
                ('subdiary','=',False),
                ('voucher_date','=',False),
                ('voucher_number','=',False),
            ])
            if settlements:
                for line in settlements:
                    _logger.info('\n\n\n subdiary: %s \n\n\n', subdiary)
                    _logger.info('\n\n\n voucher_date: %s \n\n\n', voucher_date)
                    _logger.info('\n\n\n voucher_number: %s \n\n\n', voucher_number)
                    _logger.info('\n\n\n line.document: %s \n\n\n', line.document)
                    _logger.info('\n\n\n line.id: %s \n\n\n', line.document)
                    _logger.info('\n\n\n line.requirement_id.name: %s \n\n\n', line.requirement_id.name)
                    try:
                        line.write({
                            'subdiary': subdiary,
                            'voucher_date': voucher_date,
                            'voucher_number': str(voucher_number).zfill(6),
                        })
                    except:
                        pass
        self.state = 'done'
        return True


    def update_detraction_from_xlsx(self):
        if not self.file_document:
            raise ValueError(_('There is no detraction file.'))
        decoded_file = base64.b64decode(self.file_document)
        excel_file = io.BytesIO(decoded_file)
        df = pd.read_excel(excel_file, header=1)
        for index, row in df.iterrows():
            ruc = row['DNI/RUC']
            documento = row['DOCUMENTO']
            detraction_document = row['N° DE CONSTANCIA']
            detraction_date = row['FECHA PAGO DT']
            if pd.isna(detraction_date):
                detraction_date = False
            else:
                detraction_date = detraction_date.date() if isinstance(detraction_date, pd.Timestamp) else detraction_date
            settlements = self.env['settlement'].search([
                ('dni_ruc','=',ruc),
                ('document','=',documento),
                ('detraction_document','=',False),
                ('detraction_date','=',False),
            ])
            if settlements:
                for line in settlements:
                    try:
                        line.write({
                            'detraction_document': detraction_document,
                            'detraction_date': detraction_date,
                        })
                    except:
                        pass
        self.state = 'done'
        return True

    # def update_subdiary_settlement_from_xlsx(self):
    #     if not self.file_subdiary:
    #         raise ValueError(_('There is no subdiary file.'))
    #     decoded_file = base64.b64decode(self.file_subdiary)
    #     excel_file = io.BytesIO(decoded_file)
    #     df = pd.read_excel(excel_file)
    #     for index, row in df.iterrows():
    #         ruc = row['DNI/RUC']
    #         document = row['Documento']
    #         subdiary = row['SUBDIARIOS']
    #         voucher = row['COMPROBANTE']
    #         settlement = self.env['settlement'].search([
    #             ('dni_ruc','=',ruc),
    #             ('document','=',document),
    #             ('subdiary','=',False),
    #             ('voucher_number','=',False),
    #         ], limit=1)
    #         if settlement:
    #             try:
    #                 settlement.write({
    #                     'subdiary': subdiary,
    #                     'voucher_number': voucher,
    #                 })
    #             except:
    #                 pass
    #     self.state = 'done'
    #     return True

    # def update_voucher_date_settlement_from_xlsx(self):
    #     if not self.file_dates:
    #         raise ValueError(_('There is no date file.'))
    #     decoded_file = base64.b64decode(self.file_dates)
    #     excel_file = io.BytesIO(decoded_file)
    #     df = pd.read_excel(excel_file)
    #     for index, row in df.iterrows():
    #         ruc = row['DNI/RUC']
    #         document = row['Documento']
    #         voucher_date = row['voucher_date']
    #         settlement = self.env['settlement'].search([
    #             ('dni_ruc','=',ruc),
    #             ('document','=',document),
    #             ('voucher_date','=',False),
    #         ], limit=1)
    #         if settlement:
    #             try:
    #                 settlement.write({
    #                     'voucher_date': voucher_date,
    #                 })
    #             except:
    #                 pass
    #     self.state = 'done'
    #     return True
