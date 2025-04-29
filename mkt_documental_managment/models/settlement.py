from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.addons.mkt_documental_managment.models.api_dni import apiperu_dni
from odoo.addons.mkt_documental_managment.models.api_ruc import apiperu_ruc
from odoo.addons.mkt_documental_managment.models.cpe_consult import apiperu_cpe
from dateutil.relativedelta import relativedelta
import io
import PyPDF2
from PyPDF2.utils import PdfReadError
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os
import pandas as pd

import logging

_logger = logging.getLogger(__name__)

cpe_states = [
    ('to_validate','TO VALIDATE'),
    ('accepted','ACCEPTED'),
    ('non_existent','NON EXISTENT'),
    ('failed', 'FAILED'),
]

payment_types = [
    ('spent_amount', 'Spent Amount'),
    ('real_currency', 'Real Currency')
]

document_currencies = [
        ('soles', 'Soles'),
        ('dolares', 'Dolares')
    ]

def get_default_tax(self):
    return self.env['tax.taxes'].search([('name','=','IGV(18%)')]).id


class Settlement(models.Model):
    _name = 'settlement'
    _description = 'Settlement'
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = 'settle_no asc'

    settle_no = fields.Integer(string='No.')
    requirement_id = fields.Many2one(comodel_name='documental.requirements', string='Requirement')
    repeated = fields.Boolean(default=False, string='Repeated')
    handler = fields.Integer(string='Handler')
    date = fields.Date(default=datetime.now(), string='Date')
    dni_ruc = fields.Char(string='DNI/RUC')
    partner = fields.Char(string='Partner')
    paid_to = fields.Many2one(related='requirement_id.paid_to', store=True)
    document_type_id = fields.Many2one(comodel_name='settlement.line.type', string='Document type', domain="[('visible_in_liquidation', '=', True)]", default=lambda self: self._default_document_type(), store=True)
    mobility_id = fields.Many2one(comodel_name='documental.mobility.expediture', domain="[('used','=',False)]", string='Mobility')
    document = fields.Char(string='Document')
    movement_number = fields.Char(string='Movement number')
    document_file = fields.Binary(string='File')
    document_filename = fields.Char(compute='_compute_filename', string='Filename', store=True)
    reason = fields.Char(string='Reason')
    service_type_id = fields.Many2one(comodel_name='requirement.service.type', string='Service type')
    settle_amount = fields.Float(digits=(10,3), string='Demanded amount')
    settle_igv = fields.Float(digits=(10,3), string='Demanded IGV')

    currency_id = fields.Many2one(related='requirement_id.currency_id', string='Currency')
    amount = fields.Float(compute='_compute_amount', string='Computed Amount', store=True)
    # vendor = fields.Float(compute='_compute_vendor', string='To pay', store=True)
    # detraction = fields.Float(compute='_compute_detraction_retention', string='Detraction', store=True)
    # retention = fields.Float(compute='_compute_detraction_retention', string='Retention', store=True)
    vendor = fields.Float(compute='_compute_amounts', string='To pay', store=True)
    detraction = fields.Float(compute='_compute_amounts', string='Detraction', store=True)
    retention = fields.Float(compute='_compute_amounts', string='Retention', store=True)

    tax_id = fields.Many2one(comodel_name='tax.taxes', default=get_default_tax, domain="[('tax_type','=','igv')]", string='Tax')
    igv_included = fields.Boolean(default=True, string='Included IGV?')

    income_tax = fields.Boolean(default=False, string='Income tax', tracking=True)
    income_tax_id = fields.Many2one(comodel_name='tax.taxes', domain="[('tax_type','=','income_tax')]", string='Income tax', tracking=True)

    state = fields.Selection(related='requirement_id.settlement_state', string='State', store=True)
    cpe_state = fields.Selection(selection=cpe_states, default='to_validate', string='CPE STATES')
    cpe_company_state = fields.Char(string='CPE Company State')
    line_ids = fields.One2many('settlement.line', 'settlement_id', string='Settlement line')

    journal_ids = fields.One2many('settlement.journal', 'settlement_id', string='Journal items')

    subdiary = fields.Char(string="Subdiary", size=4, tracking=True)
    voucher_number = fields.Char(string="Voucher Number", size=6, tracking=True)
    voucher_date = fields.Date(string="Voucher Date", tracking=True)
    currency = fields.Selection(string="Currency", related="requirement_id.amount_currency_type", store=True)
    main_gloss = fields.Char(string="Main gloss")
    conversion_type = fields.Char(string="Conversion type", default='V', size=1)
    flag_currency_conversion = fields.Char(string="Flag currency conversion", default='S', size=1)
    exchange_type_date = fields.Date(string="Exchange type date")
    change_type = fields.Float(string="Change type", digits=(10,3))
    document_type_code = fields.Char(string="Document type code", related="document_type_id.short_name", store=True)
    document_accountable = fields.Boolean(string="Accountable document", related="document_type_id.accountable")
    due_date = fields.Date(string="Due date")

    detail_gloss = fields.Char(string="Detail gloss", size=30)

    detraction_document = fields.Char(string='Detraction document')
    detraction_date = fields.Date(string='Detraction date')
    accountable_month_id = fields.Many2one(comodel_name='months', domain="[('open_month','=',True)]", string='Accountable month')
    accountable_year_id = fields.Many2one(comodel_name='years', domain="[('open_year','=',True)]", string='Accountable Year')
    accounting_account = fields.Char(copy=False, string="accounting account", store=True)

    differentiated_payment = fields.Boolean(default=False, string='Differentiated payment')
    payment_type = fields.Selection(selection=payment_types, string='Motive')
    wrong_payment = fields.Boolean(default=False, string='Wrong payment')
    wrong_why = fields.Char(copy=False, string="Why?", store=True)
    settle_amount_wrong = fields.Monetary(string="Settle Amount")
    alternative_amount = fields.Float(string="Alternative Amount")
    alternative_igv = fields.Float(string='Alternative IGV', digits=(10,3), default=0.00)
    document_currency = fields.Selection(selection=document_currencies, string='Document Currency')
    settle_igv_sum = fields.Float(compute='_compute_settle_igv_sum', store=True)
    settle_amount_sum = fields.Float(compute='_compute_settle_amount_sum', store=True)
    vendor_sum = fields.Float(compute='_compute_vendor_sum', store=True)
    cost_center_id = fields.Many2one('cost.center', string='CC Number', related='requirement_id.cost_center_id', store=True, readonly=True, copy=False)


    @api.depends('document_type_id', 'settle_igv')
    def _compute_settle_igv_sum(self):
        for rec in self:
            rec.settle_igv_sum = -rec.settle_igv if rec.document_type_id.id == 3 else rec.settle_igv


    @api.depends('document_type_id', 'settle_amount')
    def _compute_settle_amount_sum(self):
        for rec in self:
            rec.settle_amount_sum = -rec.settle_amount if rec.document_type_id.id == 3 else rec.settle_amount


    @api.depends('document_type_id', 'vendor')
    def _compute_vendor_sum(self):
        for rec in self:
            rec.vendor_sum = -rec.vendor if rec.document_type_id.id == 3 else rec.vendor


    @api.onchange('wrong_payment')
    def _onchange_wrong_payment(self):
        if self.wrong_payment:
            self.settle_amount = 0.0
        else:
            self.settle_amount_wrong = 0.0


    @api.onchange('requirement_id')
    def _onchange_requirement_id(self):
        if self.requirement_id:
            self.document_currency = self.requirement_id.amount_currency_type


    @api.onchange('payment_type')
    def _onchange_payment_type(self):
        if not self.payment_type:
            self.alternative_amount = 0.0


    @api.model
    def _default_document_type(self):
        return self.env['settlement.line.type'].search([('name', '=', 'FACTURA')], limit=1).id


    @api.onchange('mobility_id', 'document_type_id')
    def _onchange_document_type(self):
        for rec in self:
            zero_igv_id = rec.env['tax.taxes'].search([('percentage', '=', 0)]).id
            if rec.document_type_code == 'PM' and rec.mobility_id:
                rec.document = rec.mobility_id.name
                rec.dni_ruc = rec.mobility_id.dni
                rec.date = rec.mobility_id.date
                rec.settle_amount = rec.mobility_id.amount_total
                rec.tax_id = zero_igv_id
            else:
                rec.mobility_id = False

    @api.onchange('paid_to', 'document_type_id', 'requirement_id.dni_or_ruc')
    def compute_accounting_account(self):
        for rec in self:
            if not rec.document_type_id:
                rec.accounting_account = ''
                continue

            currency = rec.document_currency or rec.requirement_id.amount_currency_type

            if rec.document_type_id.id in [1, 3, 6, 10, 13, 18]:
                rec.accounting_account = '421201' if currency == 'soles' else '421202' if currency == 'dolares' else ''
            elif rec.document_type_id.id == 14:
                rec.accounting_account = '424101' if currency == 'soles' else '424102' if currency == 'dolares' else ''
            elif rec.document_type_id.id in [11, 31]:
                rec.accounting_account = '633028' if rec.paid_to.province_id.name == 'Lima' else '633029'
            elif rec.document_type_id.id == 22:
                rec.accounting_account = '141301' if rec.paid_to.province_id.name == 'Lima' else '141303'
            elif rec.document_type_id.id in [2, 5, 7, 24, 26]:
                rec.accounting_account = '633060'
            elif rec.document_type_id.id == 16:
                if "IMPUESTO PREDIAL" in (rec.partner or ""):
                    rec.accounting_account = '643201'
                elif "COPIA LITERAL" in (rec.requirement_id.concept or ""):
                    rec.accounting_account = '644305'
                else:
                    rec.accounting_account = '633051' if rec.paid_to.province_id.name == 'Lima' else '633052'
            elif rec.document_type_id.id in [8, 12, 25, 32, 33]:
                if len(rec.requirement_id.dni_or_ruc or '') == 8:
                    rec.accounting_account = '143101' if rec.paid_to.province_id.name == 'Lima' else '141303'
                elif len(rec.requirement_id.dni_or_ruc or '') == 11:
                    rec.accounting_account = '422101'
                else:
                    rec.accounting_account = ''
            else:
                rec.accounting_account = ''

    @api.onchange('accountable_month_id', 'accountable_year_id')
    def _onchange_accountable_month(self):
        if self.subdiary and self.accountable_month_id and self.accountable_year_id:
            domain = [
                ('accountable_month_id', '=', self.accountable_month_id.id),
                ('accountable_year_id', '=', self.accountable_year_id.id),
                ('subdiary', '=', self.subdiary),
            ]
            voucher_number_before = self.env['settlement'].search(domain, limit=1, order='voucher_number desc').voucher_number
            if voucher_number_before:
                new_number = str(int(voucher_number_before[2:6]) + 1).zfill(4)
                self.voucher_number = voucher_number_before[:2] + new_number
            else:
                self.voucher_number = self.accountable_month_id.number + '0001'


    @api.constrains('subdiary','voucher_number')
    def validate_sequence_unique(self):
        for rec in self:
            if rec.voucher_date:
                current_year = rec.voucher_date.year
                if rec.subdiary and rec.voucher_number:
                    duplicated_records = self.env['settlement'].search([
                        ('subdiary','=',rec.subdiary),
                        ('voucher_number','=',rec.voucher_number),
                        ('id','!=',rec.id),
                        ('voucher_date', '>=', f'{current_year}-01-01'),
                        ('voucher_date', '<=', f'{current_year}-12-31'),
                    ])
                    if duplicated_records:
                        raise ValidationError( _('The voucher number %s is repeated for the %s subdiary') % ( rec.voucher_number, rec.subdiary ) )
            else:
                raise ValidationError('Please enter a voucher date beforehand.')

    def download_files(self):
        combined_pdf_writer = PyPDF2.PdfFileWriter()

        for rec in self:
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', rec._name),
                ('res_id', '=', rec.id),
            ])
            
            for attachment in attachments:
                if attachment.name.lower().endswith('.pdf') or attachment.mimetype == 'application/pdf':
                    try:
                        pdf_data = io.BytesIO(base64.b64decode(attachment.datas))
                        pdf_reader = PyPDF2.PdfFileReader(pdf_data)

                        if pdf_reader.isEncrypted:
                            _logger.warning("PDF %s is encrypted and cannot be processed.", attachment.name)
                            raise ValidationError(_(
                                'The document %s is encrypted and cannot be processed.'
                            ) % attachment.name)

                        # Aplicar marca de agua por cada página
                        temp_output = io.BytesIO()
                        pdf_writer = PyPDF2.PdfFileWriter()

                        for page_num in range(pdf_reader.numPages):
                            page = pdf_reader.getPage(page_num)
                            try:
                                page.merge_page(self._create_watermark_page(rec.subdiary, rec.voucher_number))
                            except AttributeError:
                                page.mergePage(self._create_watermark_page(rec.subdiary, rec.voucher_number))  # fallback para versiones viejas
                            pdf_writer.addPage(page)

                        pdf_writer.write(temp_output)
                        temp_output.seek(0)

                        # Leer el PDF con marca de agua y agregarlo al combinado
                        marked_pdf_reader = PyPDF2.PdfFileReader(temp_output)
                        for page_num in range(marked_pdf_reader.numPages):
                            combined_pdf_writer.addPage(marked_pdf_reader.getPage(page_num))

                    except PdfReadError as e:
                        _logger.error("Error reading PDF %s: %s", attachment.name, str(e))
                        raise ValidationError(_(
                            'The document %s on the record #%s could not be read. Please convert to PDF/A format.'
                        ) % (attachment.name, rec.display_name or rec.id))

                    except Exception as e:
                        _logger.exception("Unexpected error processing PDF %s", attachment.name)
                        raise ValidationError(_(
                            'The document %s on the record #%s is not available. Please convert to PDF/A. Error: %s'
                        ) % (attachment.name, rec.display_name or rec.id, str(e)))

        output_pdf = io.BytesIO()
        combined_pdf_writer.write(output_pdf)
        output_pdf.seek(0)

        combined_pdf_attachment = self.env['ir.attachment'].create({
            'name': 'Invoices',
            'datas': base64.b64encode(output_pdf.read()),
            'type': 'binary',
            'mimetype': 'application/pdf',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % combined_pdf_attachment.id,
            'target': 'new',
        }


    def _create_watermark_page(self, subdiary, voucher_number, cost_center_id):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFontSize(12)
        can.setFillColor('Green')
        can.drawString(10, 5, '%s | %s' % (subdiary, voucher_number) )
        can.drawString(500, 5, 'CC: %s' % (cost_center_id.code or ''))
        can.save()
        packet.seek(0)
        return PyPDF2.PdfFileReader(packet).getPage(0)


    def get_last_month_domain(self):
        today = fields.Date.context_today(self)
        first_day_last_month = today + relativedelta(months=-1, day=1)
        return [
            '|',
            ('date', '>=', first_day_last_month),
            ('state', 'not in', ('refused', 'draft'))
        ]


    def get_settlement_proof_of_purchase_action(self):
        domain = [('document_type_id.proof_purchase','=',True)] + self.get_last_month_domain()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Vouchers',
            'res_model': 'settlement',
            'view_mode': 'tree,form',
            'views': [
                (self.env.ref('mkt_documental_managment.view_settlement_tree').id, 'tree'),
                (self.env.ref('mkt_documental_managment.view_accounting_settlement_form').id, 'form'),
            ],
            'domain': domain,
        }


    def attach_files(self):
        attachments = []
        for rec in self:
            if rec.document_file:
                attach = {
                    'name': rec.document_filename,
                    'datas': rec.document_file,
                    'store_fname': rec.document_filename,
                    'res_model': rec._name,
                    'res_id': rec.id,
                    'type': 'binary',
                }
                attachment = self.env['ir.attachment'].create(attach)
                attachments.append(attachment.id)


    # def cpe_validation(self):
    #     invoices = self.env['settlement'].search([
    #         ('state','in',('administration','settled')),
    #         ('cpe_state','!=','accepted'),
    #         ('requirement_id.active','=',True),
    #         ('document_type_id.short_name','=','FT'),
    #     ], order='requirement_id desc')
    #     _logger.info('\n\n\n invoices: %s \n\n\n', invoices.mapped('requirement_id.name'))
    #     for line in invoices:
    #         if (fields.Date.today() - line.date).days >= 5:
    #             line.validation_voucher()


    def validation_voucher(self):
        for rec in self:
            if rec.document_type_id.short_name == 'FT':
                cpe_data = apiperu_cpe(
                    rec.dni_ruc, 
                    '01', 
                    (rec.document.split('-')[0]).upper(), 
                    rec.document.split('-')[1].lstrip('0'), 
                    rec.date.strftime("%Y-%m-%d"), 
                    rec.settle_amount
                )
                if cpe_data and cpe_data.get('data'):
                    cpe_data_detail = cpe_data['data']
                    if cpe_data_detail and 'comprobante_estado_codigo' in cpe_data_detail:
                        if cpe_data_detail['comprobante_estado_codigo'] == '1':
                            rec.cpe_state = 'accepted'
                        else:
                            rec.cpe_state = 'non_existent'
                        
                        # Asignar el estado de la empresa como texto
                        if 'empresa_estado_descripcion' in cpe_data_detail:
                            rec.cpe_company_state = cpe_data_detail['empresa_estado_descripcion']
                    else:
                        rec.cpe_state = 'failed'
                        rec.cpe_company_state = 'Desconocido'  # Valor predeterminado si no hay estado de empresa
                else:
                    rec.cpe_state = 'failed'
                    rec.cpe_company_state = 'Desconocido'  # Valor predeterminado si no hay datos de la API


    @api.onchange('exchange_type_date')
    def _onchange_change_type(self):
        change_type_record = self.env['change.type'].search([('date','=',self.exchange_type_date)])
        if change_type_record:
            self.change_type = change_type_record.sell


    def fill_main_gloss(self):
        partner = ''
        document_type_code = ''
        document = ''
        for rec in self:
            if rec.partner:
                partner = rec.partner[:15]
            if rec.document_type_code:
                document_type_code = rec.document_type_code
            if rec.document:
                document = rec.document
            rec.main_gloss = partner + ',' + document_type_code + ' ' + document


    def update_journals(self):
        self.fill_main_gloss()
        account_invoices_soles = self.env['account.account'].search([('code','=','421201')])
        account_invoice_dolares = self.env['account.account'].search([('code','=','421202')])
        for rec in self:
            account_id = account_invoices_soles.id if rec.document_currency == 'soles' else account_invoice_dolares.id
            if not account_id:
                account_id = account_invoices_soles.id if rec.currency == 'soles' else account_invoice_dolares.id
            values_total_amount = {
                'name': 'Total amount',
                'account_id': account_invoices_soles.id if rec.document_currency == 'soles' else account_invoice_dolares.id,
                'debit': 0.00,
                'credit': rec.settle_amount,
                'annex_code': rec.dni_ruc,
                'document_number': rec.document,
            }          
            values_detraction_credit = {
                'name': _('Detraction'),
                'account_id': self.env['account.account'].search([('code','=','421203')]).id,
                'debit': 0.00,
                'credit': rec.detraction,
                'rate_type': rec.tax_id.name,
                'annex_code': rec.dni_ruc,
                'document_number': rec.detraction_document or rec.document,
                'detraction_retention_type': rec.tax_id.percentage,
                'soles_detraction_retention_amount': rec.settle_amount,
                'reference_document_type': rec.document_type_id.short_name,
                'reference_document_number': rec.document,
                'reference_document_date': rec.date,
            }
            values_igv = {
                'name': 'IGV',
                'account_id': rec.env['account.account'].search([('code','=','401111')]).id,
                'debit': rec.settle_igv,
                'credit': 0.00,
                'annex_code': False,
                'document_number': rec.document,
            }
            values_detraction_debit = {
                'name': _('Detraction'),
                'account_id':account_invoices_soles.id if rec.currency == 'soles' else account_invoice_dolares.id,
                'debit': rec.detraction,
                'credit': 0.00,
                'annex_code': rec.dni_ruc,
                'document_number': rec.document,
            }
            values_base_amount = {
                'name': _('Amount Base'),
                'account_id': False,
                'cost_center_id': rec.requirement_id.cost_center_id.id,
                # 'debit': rec.settle_amount if rec.settle_igv == 0 else rec.settle_amount / 1.18,
                'debit': rec.settle_amount if rec.settle_igv == 0 else rec.settle_amount - rec.settle_igv,
                'credit': 0.00,
                'annex_code': rec.dni_ruc,
                'document_number': rec.document,
            }
            rec.journal_ids = [(5,0,0)]
            rec.journal_ids = [(0,0,values_base_amount)]
            rec.journal_ids = [(0,0,values_total_amount)]
            if rec.detraction:
                rec.journal_ids = [(0,0,values_detraction_credit)]
                rec.journal_ids = [(0,0,values_detraction_debit)]
            if rec.settle_igv > 0:
                rec.journal_ids = [(0,0,values_igv)]


    # def compute_detraction_retention(self):
        # self._compute_detraction_retention()
        # self._compute_vendor()


    def button_compute_amounts(self):
        self._compute_amounts()


    def compute_amounts(self):
        for rec in self.line_ids:
            rec._compute_base_amount()
            rec._compute_igv()
            rec._compute_amount()


    # * Onchange methods
    @api.onchange('tax_id')
    def _onchange_tax(self):
        for rec in self.line_ids:
            rec.tax_id = self.tax_id.id


    @api.onchange('igv_included')
    def _onchange_igv_included(self):
        for rec in self.line_ids:
            rec.igv_included = self.igv_included


    @api.onchange('dni_ruc')
    def _onchange_dni_ruc(self):
        if self.dni_ruc:
            partner_name = self.env['res.partner'].search([('vat','=',self.dni_ruc)]).name
            if partner_name:
                self.partner = partner_name
            else:
                if len( self.dni_ruc ) == 8:
                    self.partner = apiperu_dni( self.dni_ruc )
                if len( self.dni_ruc ) == 11:
                    self.partner = apiperu_ruc( self.dni_ruc )[3]
        else:
            self.partner = False


    # * Compute methods
    @api.depends('date',
                 'reason',
                 'dni_ruc',
                 'document',
                 'settle_igv',
                 'document_file',
                 'settle_amount',
                 'document_type_id')
    def _compute_filename(self):
        for rec in self:
            if rec.document_file and rec.dni_ruc and rec.document:
                rec.document_filename = rec.dni_ruc + '-' + rec.document

    @api.depends('line_ids',
                 'line_ids.amount',
                 'line_ids.service_type_id',
                 'line_ids.quantity',
                 'line_ids.unit_price',
                 'line_ids.tax',
                 'line_ids.igv_included',
                 'line_ids.tax_id')
    def _compute_amount(self):
        for rec in self:
            if rec.line_ids:
                rec.amount = round( sum( rec.line_ids.mapped('amount') ), 2 )
            else:
                rec.amount = 0.00


    # @api.depends('line_ids',
    #              'line_ids.amount',
    #              'line_ids.service_type_id',
    #              'line_ids.quantity',
    #              'line_ids.unit_price',
    #              'line_ids.tax',
    #              'line_ids.igv_included',
    #              'line_ids.tax_id',
    #              'requirement_id.amount_currency_type')
    # def _compute_detraction_retention(self):
    #     for rec in self:
    #         if rec.line_ids:
    #             if rec.requirement_id.amount_currency_type == 'soles':
    #                 max_amount_line = max( rec.line_ids, key = lambda r : r.amount )
    #                 amount = sum(rec.line_ids.mapped('amount'))
    #                 if amount > max_amount_line.service_type_id.amount_from:
    #                     detraction_retention = round(
    #                         ( max_amount_line.service_type_id.percentage * amount ) / 100, 0
    #                     )
    #                     retention = round(
    #                         ( max_amount_line.service_type_id.percentage * amount ) / 100, 2
    #                     )
    #                     if max_amount_line.service_type_id.detraction:
    #                         rec.detraction = detraction_retention
    #                         rec.retention = 0.00
    #                     elif max_amount_line.service_type_id.retention:
    #                         rec.detraction = 0.00
    #                         rec.retention = retention
    #                     else:
    #                         rec.detraction = 0.00
    #                         rec.retention = 0.00
    #                 else:
    #                     rec.detraction = 0.00
    #                     rec.retention = 0.00
    #             if rec.requirement_id.amount_currency_type == 'dolares':
    #                 max_amount_line = max( rec.line_ids, key = lambda r : r.amount )
    #                 amount = sum(rec.line_ids.mapped('amount'))
    #                 sale_change_type = self.env['change.type'].search([('date','=',rec.date)]).mapped('sell')
    #                 if len(sale_change_type) == 0:
    #                     change_type = 0.00
    #                 else:
    #                     change_type = sale_change_type[0]
    #                 if amount * change_type > max_amount_line.service_type_id.amount_from:
    #                     detraction_retention = round(
    #                         ( max_amount_line.service_type_id.percentage * amount ) / 100, 0
    #                     )
    #                     retention = round(
    #                         ( max_amount_line.service_type_id.percentage * amount ) / 100, 2
    #                     )
    #                     if max_amount_line.service_type_id.detraction:
    #                         rec.detraction = detraction_retention
    #                         rec.retention = 0.00
    #                     elif max_amount_line.service_type_id.retention:
    #                         rec.detraction = 0.00
    #                         rec.retention = retention
    #                     else:
    #                         rec.detraction = 0.00
    #                         rec.retention = 0.00
    #                 else:
    #                     rec.detraction = 0.00
    #                     rec.retention = 0.00
    #         else:
    #             rec.detraction = 0.00
    #             rec.retention = 0.00


    # @api.depends('line_ids',
    #              'line_ids.amount',
    #              'line_ids.service_type_id',
    #              'line_ids.quantity',
    #              'line_ids.unit_price',
    #              'line_ids.tax',
    #              'line_ids.igv_included',
    #              'line_ids.tax_id',
    #              'requirement_id.amount_currency_type')
    # def _compute_vendor(self):
    #     for rec in self:
    #         amount = sum(rec.line_ids.mapped('amount'))
    #         max_amount_detail = rec.line_ids and max( rec.line_ids, key = lambda r : r.amount )
    #         detraction_retention = 0.00
    #         retention = 0.00
    #         if max_amount_detail:
    #             if rec.requirement_id.amount_currency_type == 'soles':
    #                 detraction_retention = round( ( max_amount_detail.service_type_id.percentage * amount ) / 100, 0 )
    #                 retention = round( ( max_amount_detail.service_type_id.percentage * amount ) / 100, 2 )
    #                 if rec.line_ids:
    #                     if amount > max_amount_detail.service_type_id.amount_from:
    #                         if max_amount_detail.service_type_id.detraction:
    #                             rec.vendor = amount - detraction_retention
    #                         elif max_amount_detail.service_type_id.retention:
    #                             rec.vendor = amount - retention
    #                         else:
    #                             rec.vendor = amount
    #                     else:
    #                         rec.vendor = amount
    #                 else:
    #                     rec.vendor = amount
    #             if rec.requirement_id.amount_currency_type == 'dolares':
    #                 sale_change_type = self.env['change.type'].search([('date','=',rec.date)]).mapped('sell')
    #                 detraction_retention = round( ( max_amount_detail.service_type_id.percentage * amount ) / 100, 0 )
    #                 retention = round( ( max_amount_detail.service_type_id.percentage * amount ) / 100, 2 )
    #                 if len(sale_change_type) == 0:
    #                     change_type = 0.00
    #                 else:
    #                     change_type = sale_change_type[0]
    #                 if rec.line_ids:
    #                     if amount * change_type > max_amount_detail.service_type_id.amount_from:
    #                         if max_amount_detail.service_type_id.detraction:
    #                             rec.vendor = amount - detraction_retention
    #                         elif max_amount_detail.service_type_id.retention:
    #                             rec.vendor = amount - retention
    #                         else:
    #                             rec.vendor = amount
    #                     else:
    #                         rec.vendor = amount
    #                 else:
    #                     rec.vendor = amount
    #         else:
    #             rec.vendor = 0


    @api.depends('currency_id', 'requirement_id', 'service_type_id', 'settle_amount', 'alternative_amount', 'differentiated_payment', 'date', 'settle_amount_sum')
    def _compute_amounts(self):
        for rec in self:
            sale_change_type = self.env['change.type'].search([('date', '=', rec.date)]).mapped('sell')
            change_type = 1
            if sale_change_type and rec.currency_id.name == 'USD':
                change_type = sale_change_type[0]
            
            effective_amount = rec.alternative_amount if rec.alternative_amount and rec.differentiated_payment else rec.settle_amount_sum

            if effective_amount * change_type > rec.service_type_id.amount_from:
                if rec.service_type_id.detraction:
                    rec.vendor = effective_amount - round((rec.settle_amount_sum * rec.service_type_id.percentage) / 100, 0)
                    rec.detraction = round((rec.settle_amount_sum * rec.service_type_id.percentage) / 100, 0)
                    rec.retention = 0.00
                elif rec.service_type_id.retention:
                    rec.vendor = effective_amount - round((rec.settle_amount_sum* rec.service_type_id.percentage) / 100, 2)
                    rec.detraction = 0.00
                    rec.retention = round((rec.settle_amount_sum * rec.service_type_id.percentage) / 100, 2)
                else:
                    rec.vendor = effective_amount
                    rec.detraction = 0.00
                    rec.retention = 0.00
            else:
                rec.vendor = effective_amount
                rec.detraction = 0.00
                rec.retention = 0.00
