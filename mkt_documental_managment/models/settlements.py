from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.addons.mkt_documental_managment.models.scraper_ruc import ConsultarRUC
from odoo.addons.mkt_documental_managment.models.api_ruc import apiperu_ruc
from odoo.addons.mkt_documental_managment.models.signature import signature_generator
import io
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64
import logging
_logger = logging.getLogger(__name__)

state = [
    ('draft', 'Draft'),
    ('waiting_boss_validation','Waiting Boss Validation'),
    ('waiting_budget_executive_validation','Waiting Budget Executive Validation'),
    ('waiting_intern_control_validation','Waiting Intern Control Validation'),
    ('waiting_administration_validation','Waiting Administration Validation'),
    ('settled','Settled'),
    ('refused','Refused')
]


def get_default_igv(self):
    return self.env['tax.taxes'].search([('name','=','IGV(18%)')]).id


def get_default_dni(self):
    vat = self.env.user.vat
    return vat


class DocumentalSettlements(models.Model):
    _name = 'documental.settlements'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Documental Settlements'
    _order = 'id desc'

    name = fields.Char(copy=False, default=lambda self: _('New'), required=True, string="FL Number")

    requirement_id = fields.Many2one(comodel_name="documental.requirements", copy=False, string="RQ Number")
    state = fields.Selection(string='State', selection=state, default='draft', tracking=True)
    responsible_id = fields.Many2one(comodel_name="res.users", string='Responsible', default=lambda self: self.env.user)
    dni = fields.Char(string='DNI', default=get_default_dni)
    value = fields.Float(string='Value', compute='compute_value')
    cost_center_id = fields.Many2one(comodel_name="cost.center", related='budget_id.cost_center_id', string='CC Number', store=True)
    balance = fields.Float(string="Balance", compute='compute_total_amount_and_balance', store=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)
    budget_id = fields.Many2one(comodel_name="budget", string='Budget Number')
    campaign_id = fields.Many2one(comodel_name="budget.campaign", related='budget_id.campaign_id', string="Activity", store=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", default=lambda self: self.env.user.employee_id)
    active = fields.Boolean(string='Active', default=True)
    refund_requirement_id = fields.Many2one(related='requirement_id.refund_requirement_id', string='Origin', copy=False)

    settlement_detail_ids = fields.One2many('documental.settlements.detail', 'documental_settlement_id', string='Settlements Details')
    restrict_settlement_detail_ids = fields.One2many('documental.settlements.detail', 'documental_settlement_id', string='Settlements Details')
    total_amount_sum = fields.Float(string="Total Amount", compute='compute_total_amount_and_balance', store=True, tracking=True)
    total_amount_char = fields.Char(string='Total amount char', compute='_compute_total_amount_char', store=True)
    amount_currency_type = fields.Selection(string="Currency", related="requirement_id.amount_currency_type", store=True)

    petitioner_signature = fields.Binary(string="Petitioner", copy=False, attachment=True)
    boss_signature = fields.Binary(string="Executive", copy=False, attachment=True)
    budget_executive_signature = fields.Binary(string="Budget Executive", copy=False, attachment=True)
    intern_control_signature = fields.Binary(string="Intern Control", copy=False, attachment=True)
    administration_signature = fields.Binary(string="Adminsitration", copy=False, attachment=True)
    is_petitioner_signed = fields.Boolean(default=False, copy=False, tracking=True)
    is_boss_signed = fields.Boolean(default=False, copy=False, tracking=True)
    is_budget_executive_signed = fields.Boolean(default=False, copy=False, tracking=True)
    is_intern_control_signed = fields.Boolean(default=False, copy=False, tracking=True)
    is_administration_signed = fields.Boolean(default=False, copy=False, tracking=True)
    petitioner_signed_on = fields.Datetime(string="Signed by Petitioner On", copy=False, tracking=True)
    boss_signed_on = fields.Datetime(string="Signed by Boss On", copy=False, tracking=True)
    budget_executive_signed_on = fields.Datetime(string="Signed by budget executive on", copy=False, tracking=True)
    intern_control_signed_on = fields.Datetime(string="Signed by Intern Control On", copy=False, tracking=True)
    administration_signed_on = fields.Datetime(string="Signed by Administration On", copy=False, tracking=True)
    user_boss_signed_id = fields.Many2one(comodel_name='res.users', copy=False, string='User boss signed')
    user_budget_executive_signed_id = fields.Many2one(comodel_name='res.users', copy=False, string='User executive signed')
    user_intern_control_signed_id = fields.Many2one(comodel_name='res.users', copy=False, string='User intern control signed')
    user_administration_signed_id = fields.Many2one(comodel_name='res.users', copy=False, string='User administration signed')
    report_administration_id = fields.Many2one(comodel_name="report.administration", copy=False)
    intern_control_received = fields.Datetime(string='Intern control reception')
    account_check = fields.Boolean(string="Account Check", copy=False, default=False)
    refund_created = fields.Boolean(default=False, string='Refund created')
    is_validated = fields.Boolean(default=False, string='Is validated')

    rq_paid_to_id = fields.Many2one(comodel_name="res.partner", string="Paid to", related="requirement_id.paid_to", store=True)
    rq_dni_or_ruc = fields.Char(string="DNI or RUC", related="requirement_id.dni_or_ruc")
    rq_detraction_bank_id = fields.Many2one(comodel_name="res.bank", string="Detraction Bank", related="requirement_id.deduction_bank", store=True)
    rq_detraction_acc_number = fields.Char(string="Detraction Account Number", related="requirement_id.deduction_acc_number", store=True)
    total_detraction_char = fields.Char(string="For the sum of", related="requirement_id.detraction_amount_char", store=True)
    total_to_pay_supplier = fields.Float(string="Pay to supplier", compute="_compute_to_pay_detraction_import", store=True)
    total_detraction = fields.Float(string="Total Detraction", compute="_compute_to_pay_detraction_import", store=True)
    total_retention = fields.Float(string="Total Retention", compute="_compute_to_pay_detraction_import", store=True)
    total_import = fields.Float(string="Total Import", compute="_compute_to_pay_detraction_import", store=True)
    total_return = fields.Float(string='Total return', compute='_compute_total_return', store=True)
    refund_op_number = fields.Char(copy=False, string="Refund Operation Number")
    refund_op_date = fields.Date(copy=False, string="Refund Operation Date")
    total_lines = fields.Integer(compute='_compute_total_lines', string='Total lines', store=True)

    card_payment = fields.Boolean(string="Payment with Card", default=False)
    concept = fields.Char(string="Concept", related="requirement_id.concept", store=True)

    repeated = fields.Boolean(default=False, string='Repeated')
    repeated_document = fields.Char(string='Repeated documents')


    def update_signatures_settlements_ic(self):
        date_str = '2024-04-27'
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        settlements = self.env['documental.settlements'].search([('requirement_id','!=',False),('intern_control_signed_on','>=',date_obj)])
        for rec in settlements:
            if not rec.requirement_id.settlement_intern_control_signature:
                rec.requirement_id.settlement_intern_control_signature = rec.intern_control_signature
                rec.requirement_id.settlement_intern_control_signed_on = rec.intern_control_signed_on
                rec.requirement_id.settlement_intern_control_user_id = rec.user_intern_control_signed_id.id
                rec.requirement_id.settlement_state = 'administration'


    def update_signatures_settlement_adminsitration(self):
        date_str = '2024-04-27'
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        settlements = self.env['documental.settlements'].search([('requirement_id','!=',False),('administration_signed_on','>=',date_obj)])
        for rec in settlements:
            if not rec.requirement_id.settlement_administration_signature:
                rec.requirement_id.settlement_administration_signature = rec.administration_signature
                rec.requirement_id.settlement_administration_signed_on = rec.administration_signed_on
                rec.requirement_id.settlement_administration_user_id = rec.user_administration_signed_id.id
                rec.requirement_id.requirement_state = 'settled'
                rec.requirement_id.settlement_state = 'settled'
                rec.requirement_id.button_send_to_budget()


    def unlink_attached_files(self):
        attachments = self.env['ir.attachment'].search([
            ('res_model','=',self._name),
            ('res_id','=',self.id),
        ])
        attachments.unlink()


    def download_attach_files(self):
        combined_pdf_writer = PyPDF2.PdfFileWriter()        
        for rec in self:
            # report_pdf_data_tuple = rec.env.ref('mkt_documental_managment.report_documental_settlements').sudo()._render_qweb_pdf(rec.ids)
            # report_pdf_data = report_pdf_data_tuple[0]
            report_pdf_data_tuple_requirement = rec.env.ref('mkt_documental_managment.report_documental_requirements').sudo()._render_qweb_pdf(rec.requirement_id.ids)
            report_pdf_data_requirement = report_pdf_data_tuple_requirement[0]
            if report_pdf_data_requirement:
                report_pdf_requirement = io.BytesIO(report_pdf_data_requirement)
                report_pdf_reader_requirement = PyPDF2.PdfFileReader(report_pdf_requirement)
                for page_num in range(report_pdf_reader_requirement.numPages):
                    page_requirement = report_pdf_reader_requirement.getPage(page_num)
                    combined_pdf_writer.addPage(page_requirement)
            # if report_pdf_data:
            #     report_pdf = io.BytesIO(report_pdf_data)
            #     report_pdf_reader = PyPDF2.PdfFileReader(report_pdf)
            #     for page_num in range(report_pdf_reader.numPages):
            #         page = report_pdf_reader.getPage(page_num)
            #         combined_pdf_writer.addPage(page)
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', rec._name),
                ('res_id', '=', rec.id),
            ])
            for attachment in attachments:
                if attachment.name.lower().endswith('.pdf') or attachment.mimetype == 'application/pdf':
                    pdf_data = io.BytesIO(base64.b64decode(attachment.datas))
                    pdf_reader = PyPDF2.PdfFileReader(pdf_data)
                    for i in range(2):
                        output_pdf = io.BytesIO()
                        pdf_writer = PyPDF2.PdfFileWriter()
                        for page_num in range(pdf_reader.numPages):
                            page = pdf_reader.getPage(page_num)
                            pdf_writer.addPage(page)
                            page.mergePage(self._create_watermark_page(rec.cost_center_id.code, rec.budget_id.name, rec.requirement_id.name))
                        pdf_writer.write(output_pdf)
                        output_pdf.seek(0)
                        pdf_reader = PyPDF2.PdfFileReader(output_pdf)
                        for page_num in range(pdf_reader.numPages):
                            page = pdf_reader.getPage(page_num)
                            combined_pdf_writer.addPage(page)
        output_pdf = io.BytesIO()
        combined_pdf_writer.write(output_pdf)
        output_pdf.seek(0)
        combined_pdf_attachment = self.env['ir.attachment'].create({
            'name': 'Combined PDF.pdf',
            'datas': base64.b64encode(output_pdf.read()),
            'type': 'binary',
            'mimetype': 'application/pdf',
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % combined_pdf_attachment.id,
            'target': 'new',
        }


    def _create_watermark_page(self, code, ppto, requirement):
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)
        can.setFontSize(12)
        can.setFillColor('Green')
        can.drawString(10, 5, 'CC:%s   %s   %s' % ( code, ppto, requirement ) )
        can.save()
        packet.seek(0)
        return PyPDF2.PdfFileReader(packet).getPage(0)


    @api.onchange('settlement_detail_ids')
    def _onchange_repeated_document(self):
        text = ''
        for rec in self.settlement_detail_ids:
            stls = self.env['documental.settlements.detail'].sudo().search([('ruc','=',rec.ruc),('document_type','=',rec.document_type.id),('document','=',rec.document)]).mapped('documental_settlement_id.name')
            if self.name in stls:
                stls.remove(self.name)
            if rec.repeated:
                text += _('The %s %s is repeated on %s. \n') % (
                    rec.document_type.name,
                    rec.document,
                    ', '.join(stls)
                )
        self.repeated_document = text
        if len( self.repeated_document ) != 0:
            self.repeated = True
        else:
            self.repeated = False


    def send_email_to_validate(self):
        settlements = self.env['documental.settlements'].search([
            ('state','in',('waiting_administration_validation','settled')),
            ('is_validated','=',False),
            ('create_date','>=',datetime(2024, 1, 16).strftime('%Y-%m-%d 00:00:00')),
        ])
        for settlement in settlements:
            mail_obj = self.env['mail.mail']
            subject = 'Recodatorio para validar la liquidación %s con la SUNAT.' % ( settlement.name )
            body = '''Hola, recientemente firmaste la liquidación %s pero no validaste el estado y condición🐸\
                de aquellos RUC's en las líneas de la liquidación.\n
                Además, no se verificó si los documentos ingresados están permitidos en la SUNAT dependiendo del tipo de contribuyente que son.\n
                Recuerda que con el botón 'Validar' puedes realizar todo ello. 
                Por otro lado, puedes verificar la validez de los documentos electrónicos en el menú Utilidades > Consulta CPE \
                e ingresando la información necesaria.
            ''' % ( settlement.name )
            email_to = settlement.user_intern_control_signed_id.login
            mail = mail_obj.create({
                'subject': subject,
                'body_html': body,
                'email_to': email_to,
            })
            mail.send()


    def button_validate_document(self):
        message = ''
        self.is_validated = True
        if self.settlement_detail_ids:
            for rec in self.settlement_detail_ids:
                if rec.ruc:
                    if len(rec.ruc) == 11 and rec.document_type.is_ruc == True:
                        ruc = rec.ruc
                        message += _(' || %s:' % ( ruc if ruc else '' ))
                        raw_info = ConsultarRUC(ruc)[0]
                        info = raw_info[0]
                        print_recept_info = raw_info[1][1].replace('\n','').replace('\t','').replace('\r','').replace('</br>','').replace('<td>','').replace('</td>','').replace('<tr>','').replace('</tr>','').strip().replace(' ','')
                        if 'IMPORTANTE' in info[1]:
                            info.pop(1)
                        if 'PERSONA' not in info[1]:
                            electronic_issuance_info = info[12]
                        else:
                            electronic_issuance_info = info[13]
                        if ruc[:2] == '20' and ( 'BOLETA' in rec.document_type.name ):
                            raise ValidationError(_('A supplier with RUC %s can issue invoices, but you are selected a sales receipt. Instead, the supplier must issue an invoice.') % (ruc))
                        if ruc[:2] == '10' and ( 'BOLETA' in rec.document_type.name ) and ('FACTURA' in print_recept_info + electronic_issuance_info):
                            raise ValidationError(_('A supplier with RUC %s can issue invoices, but you are selected a sales receipt. Please, modify the line in the Settlement detail.') % (ruc))
                        if ruc[:2] == '10' and rec.document_type.name == 'FACTURA' and ('FACTURA' not in print_recept_info + electronic_issuance_info):
                            raise ValidationError(_('The supplier with RUC %s cannot issue invoices. Please select a sales receipt.') % (ruc))
                        for i in range(0,8):
                            info[i] = info[i].replace('\n','').replace('\t','').replace('\r','').replace('</br>','')
                        if 'PERSONA' not in info[1]:
                            message += _(' %s -' % ( info[5] if info[5] else ''))
                            message += _(' %s,' % ( info[6] if info[6] else ''))
                            if (info[5] != 'ACTIVO') or (info[6] != 'HABIDO'):
                                raise ValidationError(_('The contact %s is found as %s and its condition is %s.') % (info[0].split('-')[-1].strip(), info[5].strip().replace(' ','').replace('BAJADEOFICIO','BAJA DE OFICIO - ').replace('SUSPENSIONTEMPORAL','SUSPENSION TEMPORAL').replace('BAJADEFINITIVA','BAJA DEFINITIVA - ').replace('BAJAPROV.POROFICIO','BAJA PROVICIONAL POR OFICIO - ').replace('FechadeBaja','Fecha de Baja'), info[6].split('   ')[0].strip()))
                        else:
                            message += _(' %s -' % ( info[6] if info[6] else ''))
                            message += _(' %s,' % ( info[7] if info[7] else '' ))
                            if info[6] != 'ACTIVO' or info[7] != 'HABIDO':
                                raise ValidationError(_('The contact %s is found as %s and its condition is %s.') % (info[2].split('-')[-1].strip(), info[6].strip().replace(' ','').replace('BAJADEFINITIVA','BAJA DEFINITIVA - ').replace('BAJADEOFICIO','BAJA DE OFICIO - ').replace('SUSPENSIONTEMPORAL','SUSPENSION TEMPORAL').replace('BAJAPROV.POROFICIO','BAJA PROVICIONAL POR OFICIO - ').replace('FechadeBaja','Fecha de Baja'), info[7].split('</br>')[0].split('   ')[0].strip()))
                        message += _(' %s' % ( rec.document_type.name if rec.document_type else '' ))
                        message += _(' OKAY!👌|| ')
            if len(message) > 1:
                self.message_post(
                    body=_("Validation: %s") % (message),
                )
        else:
            raise ValidationError(_('There are no lines wrote in settlement detail.'))
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': True,
            }
        }


    @api.depends('settlement_detail_ids.date',
                 'settlement_detail_ids.amount')
    def _compute_total_lines(self):
        for rec in self:
            rec.total_lines = len(rec.settlement_detail_ids)


    @api.depends('settlement_detail_ids',
                 'settlement_detail_ids.amount',
                 'settlement_detail_ids.settlement_detail_line_ids')
    def _compute_total_return(self):
        return_amount = 0.00
        for rec in self.settlement_detail_ids:
            if rec.document_type.is_return:
                return_amount += rec.amount
        self.total_return = return_amount


    @api.depends('settlement_detail_ids',
                 'settlement_detail_ids.amount',
                 'settlement_detail_ids.settlement_detail_line_ids')
    def _compute_total_amount_char(self):
        for rec in self:
            total_amount = sum(rec.settlement_detail_ids.mapped('amount'))
            total_amount_char = rec.less_than_1000000000000(round(total_amount + 0.00, 2))
            if rec.requirement_id.amount_currency_type == 'soles':
                rec.total_amount_char = ( total_amount_char.replace('uno mil','un mil') + ' soles' ).upper()
            if rec.requirement_id.amount_currency_type == 'dolares':
                rec.total_amount_char = ( total_amount_char.replace('uno mil','un mil') + ' dólares').upper()


    @api.depends('settlement_detail_ids',
                 'settlement_detail_ids.settlement_detail_line_ids',
                 'settlement_detail_ids.amount')
    def _compute_to_pay_detraction_import(self):
        for rec in self:
            rec.total_detraction = sum(rec.settlement_detail_ids.mapped('detraction_amount'))
            rec.total_retention = sum(rec.settlement_detail_ids.mapped('retention_amount'))
            rec.total_to_pay_supplier = sum(rec.settlement_detail_ids.mapped('to_pay'))
            total_import = sum(rec.settlement_detail_ids.search([('documental_settlement_id','=',rec.id),('document_type.is_return','=',False),('document_type','!=','DEVOLUCIÓN')]).mapped('amount'))
            total_return_quot = sum(rec.settlement_detail_ids.search([('documental_settlement_id','=',rec.id),('document_type.is_return','=',True)]).mapped('amount') )
            rec.total_import = total_import - total_return_quot
            # rec.total_import = sum(rec.settlement_detail_ids.search([('documental_settlement_id','=',rec.id),('document_type','!=','DEVOLUCIÓN')]).mapped('amount'))
            detraction = rec.less_than_1000000000000(rec.total_detraction)
            if rec.requirement_id.amount_soles:
                rec.total_detraction_char = (detraction.replace("uno mil", "un mil") + " soles").upper()
            elif rec.requirement_id.amount_uss:
                rec.total_detraction_char = (detraction.replace("uno mil", "un mil") + " dóalres").upper()


    def button_account_check_true(self):
        if self.account_check == False:
            self.account_check = True


    def button_account_check_false(self):
        if self.account_check == True:
            self.account_check = False


    def action_open_account_settlement(self):
        self.ensure_one()
        view = self.env.ref('mkt_documental_managment.view_settlement_account_form')
        return {
            'name': _('Account Review'),
            'type': 'ir.actions.act_window',
            'res_model': 'documental.settlements',
            'view_mode': 'form',
            'views': [(view.id, 'form')],
            'res_id': self.env['documental.settlements'].search([('id','=',self.id)]).id,
            'target': 'new',
        }


    def button_cancel(self):
        budget_lines_obj = self.env['budget.line']
        budget_lines = budget_lines_obj.search([
            ('budget_id','=',self.budget_id.id),
            ('settlement_name','=',self.name)
        ])
        budget_lines.unlink()


    def button_refuse_boss(self):
        self = self.sudo()
        if self.petitioner_signature:
            self.petitioner_signature = False
            self.is_petitioner_signed = False
        if self.boss_signature:
            self.boss_signature = False
            self.is_boss_signed = False
        if self.budget_executive_signature:
            self.budget_executive_signature = False
            self.is_budget_executive_signed = False
        if self.intern_control_signature:
            self.intern_control_signature = False
            self.is_intern_control_signed = False
        if self.administration_signature:
            self.administration_signature = False
            self.is_administration_signed = False
        self.state = 'refused' if self.state != 'draft' else 'draft'
        self.unlink_attached_files()
        menu = self.env.ref('mkt_documental_managment.doc_mng_settlements')
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }


    def button_refuse_budget_executive(self):
        self = self.sudo()
        if self.petitioner_signature:
            self.petitioner_signature = False
            self.is_petitioner_signed = False
            self.intern_control_received = False
        if self.boss_signature:
            self.boss_signature = False
            self.is_boss_signed = False
            self.intern_control_received = False
        self.state = 'refused' if self.state != 'draft' else 'draft'
        self.unlink_attached_files()
        menu = self.env.ref('mkt_documental_managment.doc_mng_settlements')
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }


    def button_refuse_intern_control(self):
        self = self.sudo()
        if self.petitioner_signature:
            self.petitioner_signature = False
            self.is_petitioner_signed = False
        if self.boss_signature:
            self.boss_signature = False
            self.is_boss_signed = False
            self.intern_control_received = False
        if self.budget_executive_signature:
            self.budget_executive_signature = False
            self.is_budget_executive_signed = False
            self.intern_control_received = False
        self.state = 'refused' if self.state != 'draft' else 'draft'
        self.unlink_attached_files()
        menu = self.env.ref('mkt_documental_managment.doc_mng_settlements')
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }


    def button_refuse_administration(self):
        self = self.sudo()
        if self.petitioner_signature:
            self.petitioner_signature = False
            self.is_petitioner_signed = False
        if self.boss_signature:
            self.boss_signature = False
            self.is_boss_signed = False
            self.intern_control_received = False
        if self.budget_executive_signature:
            self.budget_executive_signature = False
            self.is_budget_executive_signed = False
            self.intern_control_received = False
        if self.intern_control_signature:
            self.intern_control_signature = False
            self.is_intern_control_signed = False
            self.intern_control_received = False
        self.state = 'refused' if self.state != 'draft' else 'draft'
        self.unlink_attached_files()
        menu = self.env.ref('mkt_documental_managment.doc_mng_settlements')
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }


    def button_refuse_admin(self):
        self = self.sudo()
        if self.administration_signature:
            self.administration_signature = False
            self.is_administration_signed = False
        self.state = 'waiting_administration_validation'
        self.button_cancel()
        self.requirement_id.state = 'to_settle'
        menu = self.env.ref('mkt_documental_managment.doc_mng_settlements')
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
            'params': {'menu_id': menu.id},
        }


    def document_format_validation(self):
        for rec in self.settlement_detail_ids:
            if rec.document_type.national_format == True:
                if rec.document:
                    if '-' not in rec.document:
                        raise ValidationError(_("""It is necesary the '-' character in document format.\n
                            The correct document name is something like this: FFF1-00000001\n
                            It means that on left hand: Four(4) characters. On the right hand: Eight(8) characters. And no spaces between."""))
                    else:
                        serie, number = (rec.document).split('-')
                        if (len(serie) != 4) or (len(number) != 8):
                            raise ValidationError(_("""It is necesary four(4) characters on the left hand and eight(8) characters on the right hand.\n
                                The correct format document name is something like this: FFF1-00000001. And no spaces between."""))
                else:
                    raise ValidationError(_('Please, you have to fill the document name.'))


    def attach_in_chatter(self):
        attachments = []
        for line in self.settlement_detail_ids:
            if line.document_file:
                attach = {
                    'name': line.document_filename,
                    'datas': line.document_file,
                    'store_fname': line.document_filename,
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary',
                }
                attachment = self.env['ir.attachment'].create(attach)
                attachments.append(attachment.id)
        # if attachments:
        #     self.message_post(
        #         body=_('Document attached.'),
        #         attachment_ids=attachments,
        #     )
        # for line in self.settlement_detail_ids:
        #     if line.document_file:
        #         attach = {
        #             'name':line.document_filename,
        #             'datas':line.document_file,
        #             'store_fname':line.document_filename,
        #             'res_model':line._name,
        #             'res_id':line.id,
        #             'type':'binary',
        #         }
        #         self.message_post(
        #             body=_("Document file: %s") % (line.document_filename),
        #             attachment_ids=[self.env['ir.attachment'].create(attach).id],
        #         )


    def button_petitioner_signature(self):
        if self.balance < 0:
            raise ValidationError(_('The balance should be greater than or equal to zero, but is less than zero.'))
        else:
            alias_name = self.env.user.partner_id.alias_name
            user_name = alias_name if alias_name else self.env.user.name
            self.attach_in_chatter()
            self.write({
                # 'petitioner_signature': self.signature_generator(),
                'petitioner_signature': signature_generator(user_name),
                'is_petitioner_signed': True,
                'petitioner_signed_on': fields.Datetime.now(),
                'state': 'waiting_boss_validation',
            })
        if self.settlement_detail_ids:
            self.document_format_validation()
            for rec in self.settlement_detail_ids:
                if not rec.document_file:
                    raise ValidationError(_("The 'File' field is required. Be sure to upload one document for each detail line in the Settlement."))
        else:
            raise ValidationError(_('Please, make sure to write at least one line in the Settlement detail.'))


    def button_boss_signature(self):
        if not self.requirement_id.boss_signature:
            raise ValidationError(_('The requirement associated %s to this settlement has not yet been signed. Be sure to validate said requirement before signing its settlement.') % (self.requirement_id.name))
        else:
            alias_name = self.env.user.partner_id.alias_name
            user_name = alias_name if alias_name else self.env.user.name
            if self.budget_id.responsible_revision:
                self.write({
                    'boss_signature': signature_generator(user_name),
                    'is_boss_signed': True,
                    'state': 'waiting_budget_executive_validation',
                    'user_boss_signed_id': self.env.user.id,
                    'boss_signed_on': fields.Datetime.now(),
                })
            else:
                self.write({
                    'boss_signature': signature_generator(user_name),
                    'is_boss_signed': True,
                    'state': 'waiting_intern_control_validation',
                    'user_boss_signed_id': self.env.user.id,
                    'boss_signed_on': fields.Datetime.now(),
                    'intern_control_received': fields.Datetime.now(),
                })


    def button_budget_executive_signature(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        if self.budget_id.responsible_revision:
            if not self.requirement_id.budget_executive_signature:
                raise ValidationError(_('The requirement associated %s to this settlement has not yet been signed. Be sure to validate said requirement before signing its settlement.') % ( self.requirement_id.name ))
            else:
                self.write({
                    'budget_executive_signature': signature_generator(user_name),
                    'is_budget_executive_signed': True,
                    'state': 'waiting_intern_control_validation',
                    'budget_executive_signed_on': fields.Datetime.now(),
                    'user_budget_executive_signed_id': self.env.user.id,
                    'intern_control_received': fields.Datetime.now(),
                })
        else:
            self.write({
                'budget_executive_signature': signature_generator(user_name),
                'is_budget_executive_signed': True,
                'state': 'waiting_intern_control_validation',
                'budget_executive_signed_on': fields.Datetime.now(),
                'user_budget_executive_signed_id': self.env.user.id,
            })


    def button_intern_control_signature(self):
        if not self.requirement_id.intern_control_signature:
            raise ValidationError(_('The requirement associated %s to this settlement has not yet been signed. Be sure to validate said requirement before signing its settlement.') % (self.requirement_id.name))
        else:
            alias_name = self.env.user.partner_id.alias_name
            user_name = alias_name if alias_name else self.env.user.name
            for line in self.settlement_detail_ids:
                if line.document_type.name == 'DEVOLUCIÓN' and not line.movement_number:
                    raise ValidationError( _('Please, make sure to fill the movement number for RETURN document type') )
                line.attach_in_chatter()
                line.button_conversion()
                line.button_main_gloss()
                line.fill_data()
            self.requirement_id.timer_state = 'on_time'
            self.write({
                'intern_control_signature': signature_generator(user_name),
                'is_intern_control_signed': True,
                'intern_control_signed_on': fields.Datetime.now(),
                'state': 'waiting_administration_validation',
                'user_intern_control_signed_id': self.env.user.id,
            })


    def create_refund_requirement(self):
        if self.balance > 0:
            requirement = self.env['documental.requirements'].sudo().create({
                'paid_to': self.requirement_id.full_name.partner_id.id,
                'dni_or_ruc': self.requirement_id.dni,
                'budget_id': self.requirement_id.budget_id.id,
                'partner_id': self.requirement_id.partner_id.id,
                'cost_center_id': self.requirement_id.cost_center_id.id,
                'year_month_id': self.requirement_id.year_month_id.id,
                'campaign_id': self.requirement_id.campaign_id.id,
                'amount_currency_type': self.requirement_id.amount_currency_type,
                'concept': _('Request for reimbursement of expenses incurred for the benefit of the company'),
                'is_refund': True,
                'refund_user_id': self.requirement_id.full_name.id,
                # 'refund_employee_id': self.requirement_id.full_name.id,
                'refund_employee_id': self.requirement_id.full_name.employee_id.id,
                'refund_requirement_id': self.requirement_id.id,
            })
            self.env['requirement.detail.justification'].create({
                'requirement_id': requirement.id,
                'partner': self.env.user.partner_id.id,
                'reason': _('Refund'),
                'amount': self.balance,
            })
            self.activity_schedule(
                'mkt_documental_requirement.mail_action_refund_requirement',
                user_id = self.requirement_id.full_name.id,
                summary = _("Refund Requirement created: %s") % (requirement.name),
            )
            self.refund_created = True


    def button_administration_signature(self):
        if not self.requirement_id.administration_signature:
            raise ValidationError(_('The requirement associated %s to this settlement has not yet been signed. Be sure to validate said requirement before signing its settlement.') % (self.requirement_id.name))
        else:
            if self.balance > 0:
                return {
                    'name': 'Administration validation',
                    'view_mode': 'form',
                    'view_id': self.env.ref('mkt_documental_managment.view_return_requirement_confirmation_wiz_form').id,
                    'view_type': 'form',
                    'res_model': 'return.requirement.confirmation',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                }
            else:
                alias_name = self.env.user.partner_id.alias_name
                user_name = alias_name if alias_name else self.env.user.name
                self.write({
                    'administration_signature': signature_generator(user_name),
                    'is_administration_signed': True,
                    'user_administration_signed_id': self.env.user.id,
                    'state': 'settled',
                })
                self.button_send_to_budget()
                self.button_send_to_transfer()
                self.administration_signed_on = fields.Datetime.now()
                # self.create_refund_requirement()


    # def signature_generator(self):
    #     # font_path = get_module_resource('web', 'static/fonts/sign', 'Rhesmanisa.ttf')
    #     font_path = get_module_resource('web', 'static/fonts/sign', 'LaBelleAurore-Regular.ttf')
    #     font = ImageFont.truetype(font_path, 70)
    #     image = Image.new(mode='RGB', size=(600, 150), color=(255, 255, 255))
    #     draw = ImageDraw.Draw(image)
    #     user_name = self.env.user.name
    #     draw.text((10, 10), user_name.title(), font=font, fill=(0, 0, 0))
    #     buffered = BytesIO()
    #     image.save(buffered, format="PNG")
    #     img_str = base64.b64encode(buffered.getvalue()).decode()
    #     return img_str


    def button_send_to_transfer(self):
        values = {}
        report_administration = self.env['report.administration'].search([('requirement_id','=',self.requirement_id.id)])
        self.report_administration_id = report_administration.id
        self.report_administration_id.transfer_line_ids = [(5,0,0)]
        for line in self.settlement_detail_ids:
            values.update({
                'report_administration_id': report_administration.id,
                'documental_settlement_id': self.id,
                'date': line.date,
                'settlement_name': self.name,
                'document_type': line.document_type.name,
                'document_file': line.document_file,
                'document_filename': line.document_filename,
                'document': line.document,
                'reason': line.reason,
                'amount': line.amount,
            })
            self.report_administration_id.transfer_line_ids = [(0,0,values)]
        self.report_administration_id.rq_state = 'settled'


    def button_send_to_budget(self):
        if not self.budget_id:
            raise UserError(_('There is no budget for the current settlement'))
        else:
            values = {}
            for line in self.settlement_detail_ids:
                if line.document_type.budgetable == 'yes':
                    values.update({
                        'budget_id': self.budget_id.id,
                        # 'documental_settlement_id': self.id,
                        'documental_settlement_id': line.documental_settlement_id.id,
                        'date': line.date,
                        'document_type': line.document_type.name,
                        'document_file': line.document_file,
                        'document_filename': line.document_filename,
                        'document': line.document,
                        'reason': line.reason,
                        'amount': line.amount,
                        'settlement_name': self.name,
                        'settlement_detail_id': line.id,
                    })
                    self.budget_id.budget_line_ids = [(0,0,values)]
            self.state = 'settled'
            self.requirement_id.state = 'settled'


    @api.depends('requirement_id')
    def compute_value(self):
        for rec in self:
            if rec.requirement_id:
                total_soles = 0
                total_dolares = 0
                if rec.requirement_id.amount_currency_type == 'soles':
                    total_soles = rec.requirement_id.amount_soles
                    rec.value = total_soles
                if rec.requirement_id.amount_currency_type == 'dolares':
                    total_dolares = rec.requirement_id.amount_uss
                    rec.value = total_dolares
            else:
                rec.value = 0


    @api.depends('settlement_detail_ids.amount')
    def compute_total_amount_and_balance(self):
        for sett in self:
            total_amount_sum = 0.0
            total_return_sum = 0.00
            balance = 0.0
            for line in sett.settlement_detail_ids:
                if not line.document_type.is_return:
                    total_amount_sum += line.amount
                else:
                    total_return_sum += line.amount
            # total_amount_sum = total_amount_sum - 
            # balance = round(total_amount_sum - total_return_sum - sett.value, 2)
            balance = round(total_amount_sum - sett.value, 2)
            sett.update({
                'total_amount_sum': total_amount_sum - total_return_sum,
                'balance': balance
            })


    def get_date_without_decimals(self):
        for rec in self:
            rec.date = rec.create_date


    def action_print_pdf(self):
        return self.env.ref('mkt_documental_managment.report_documental_settlements').report_action(self)


    def _get_report_documental_settlement_base_filename(self):
        self.ensure_one()
        return _('Settlement - %s') % (self.name or '')


    def draft(self):
        self.state = 'draft'


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('documental.settlements') or _('New')
        return super(DocumentalSettlements, self).create(vals)


    def less_than_100(self, number):
        units = ["cero","uno","dos","tres","cuatro","cinco","seis","siete","ocho","nueve","diez","once","doce","trece","catorce","quince"]
        tens = ["","diez","veinte","treinta","cuarenta","cincuenta","sesenta","setenta","ochenta","noventa"]
        unidades = number % 10
        decenas = number // 10
        result = ""
        if number <= 15:
            result += units[number]
        else:
            if decenas == 1:
                result += "dieci"
            elif decenas == 2:
                if unidades == 0:
                    result += "veinte"
                else:
                    result += "veinti"
            else:
                result += tens[decenas]
                if unidades != 0:
                    result += " y "
            if unidades != 0:
                result += units[unidades]
        return result

    def less_than_1000(self, number):
        hundreds = ["","cien","doscientos","trescientos","cuatroscientos","quinientos","seiscientos","setecientos","ochocientos","novecientos"]
        decenas = number % 100
        centenas = number // 100
        result = ""
        if centenas != 0:
            if centenas == 1:
                if decenas == 0:
                    result += "cien"
                else:
                    result += "ciento"
            else:
                result += hundreds[centenas]
            if decenas != 0:
                result += " "
        if centenas == 0 or decenas != 0:
            result += self.less_than_100(decenas)
        return result

    def less_than_1000000(self, number):
        centenas = number % 1000
        miles = number // 1000
        result = ""
        if miles >= 2:
            result += self.less_than_1000(miles) + " "
        if miles != 0:
            result += "mil"
        if centenas != 0 or miles == 0:
            if miles != 0:
                result += " "
            result += self.less_than_1000(centenas)
        return result

    def less_than_1000000000000(self, number):
        integer_part, decimal_part = str(number).split('.')
        integer_part = int(integer_part)
        miles = integer_part % 1000000
        millones = integer_part // 1000000
        result = ""
        if millones >= 2:
            result += self.less_than_1000000(millones) + " millones"
        if millones == 1:
            result += "Un millón"
        if miles != 0 or millones == 0:
            if millones != 0:
                result += " "
            result += self.less_than_1000000(miles)
        if decimal_part in ("0","00"):
            result += " con 00/100"
        else:
            if len(decimal_part) == 1:
                result += " con " + str(decimal_part) + "0/100"
            else:
                result += " con " + str(decimal_part) + "/100"
        return result


class DocumentalSettlementsDetail(models.Model):
    _name = 'documental.settlements.detail'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'documental settlements detail'
    _order = 'id desc'

    documental_settlement_id = fields.Many2one('documental.settlements', string='Documental Settlements')
    sequence_handle = fields.Integer(string="Sequence handle")
    date = fields.Date(string='Date', default=datetime.now())
    ruc = fields.Char(string="RUC")
    partner = fields.Char(string="Partner")
    document_type = fields.Many2one(comodel_name="settlement.line.type", string="Document Type")
    document = fields.Char(string='Document', required=True)
    movement_number = fields.Char(string="Movement number")
    document_file = fields.Binary(string="File", required=True, attachment=True)
    document_filename = fields.Char(string="File Name", compute="compute_filename", store=True)
    reason = fields.Char(string='Reason')
    amount = fields.Float(string='Amount', compute="_compute_amount_detraction_to_pay_igv_base", digits=(10,2), store=True)
    to_pay = fields.Float(string="Pay to Supploer", compute="_compute_amount_detraction_to_pay_igv_base", digits=(10,2), store=True)
    detraction_amount = fields.Float(string="Detraction", compute="_compute_amount_detraction_to_pay_igv_base", store=True)
    retention_amount = fields.Float(string="Retention", compute="_compute_amount_detraction_to_pay_igv_base", store=True)
    tax_igv_id = fields.Many2one(comodel_name="tax.taxes", string="% IGV", default=get_default_igv, store=True)
    is_taxable = fields.Boolean(string="Taxable", default=True)
    igv_included = fields.Boolean(string="IGV included?", default=True)
    igv_total = fields.Float(string="Total IGV", compute="_compute_amount_detraction_to_pay_igv_base", digits=(10,2), store=True)
    base_amount_total = fields.Float(string="Total base amount", compute="_compute_amount_detraction_to_pay_igv_base", digits=(10,2), store=True)
    state = fields.Selection(string="State", selection=state, related="documental_settlement_id.state", store=True)
    cost_center_id = fields.Many2one(comodel_name="cost.center", related="documental_settlement_id.cost_center_id", string="Cost Center")
    budget_id = fields.Many2one(comodel_name="budget", related="documental_settlement_id.budget_id", string="Budget")
    settlement_detail_line_ids = fields.One2many('settlement.detail.line', 'settlement_detail', string="Settlement Detail Line")
    restricted_settlement_detail_line_ids = fields.One2many('settlement.detail.line', 'settlement_detail', string="Settlement Detail Line")
    review_in_quotation = fields.Boolean(string="Review in Quotation", default=False)
    journal_ids = fields.One2many("settlement.line.journal", "settlement_detail_id", string="Journal items")

    detraction_payment_date = fields.Date(string="Detraction payment date")
    detraction_operation_number = fields.Char(string="Detraction operation number")
    detraction_number = fields.Char(string="Detraction Number")
    detraction_file = fields.Binary(string="File", attachment=True)
    detraction_filename = fields.Char(string="File Name")

    subdiary = fields.Char(string="Subdiary", size=4)
    voucher_number = fields.Char(string="Voucher Number", size=6)
    voucher_date = fields.Date(string="Voucher Date")
    currency = fields.Selection(string="Currency", related="documental_settlement_id.requirement_id.amount_currency_type", store=True)
    main_gloss = fields.Char(string="Main gloss")
    change_type = fields.Float(string="Change type", digits=(10,3), default=0.00)
    conversion_type = fields.Char(string="Conversion type", default='V', size=1)
    flag_currency_conversion = fields.Char(string="Flag currency conversion", default='S', size=1)
    exchange_type_date = fields.Date(string="Exchange type date")
    document_type_code = fields.Char(string="Document type code", related="document_type.short_name", store=True)
    document_accountable = fields.Boolean(string="Accountable document", related="document_type.accountable")
    due_date = fields.Date(string="Due date")
    detail_gloss = fields.Char(string="Detail gloss", size=30)

    repeated = fields.Boolean(compute='_compute_repeated', default=False, string='Repeated')

    @api.depends('ruc','document_type','document')
    def _compute_repeated(self):
        for rec in self:
            triplet = self.env['documental.settlements.detail'].search(
                [
                    ('id','not in', rec.ids),
                    ('ruc','=',rec.ruc),
                    ('document_type','=',rec.document_type.id),
                    ('document','=',rec.document),
                ]
            )
            if triplet:
                rec.repeated = True
            else:
                rec.repeated = False


    # def button_download_document(self):
    #     def isBase64_decodestring(s):
    #         try:
    #             return base64.b64decode(s)
    #         except Exception as e:
    #             raise ValidationError('Error: ', + str(e))
    #     path = os.path.dirname(os.path.realpath(__file__))
    #     file_name = "static\\src\\zip_temp\\" + 'accounting_documents'
    #     file_name_zip = file_name + ".rar"
    #     zipfilepath = os.path.join(path, file_name_zip)
    #     zip_archive = zipfile.ZipFile(zipfilepath, "w")
    #     for rec in self:
    #         # object_name = rec.document_filename + '.pdf'
    #         object_name = rec.document_filename
    #         object_handle = open(object_name, "wb")
    #         object_handle.write(isBase64_decodestring(rec.document_file))
    #         object_handle.close()
    #         zip_archive.write(object_name)
    #     zip_archive.close()
    #     filename = "accounting_documents.rar"
    #     return {
    #         'type': 'ir.actions.act_url',
    #         'url': '/mkt_documental_managment/models/static/src/zip_temp/' + 'accounting_documents.rar',
    #         'target': 'new',
    #         'headers': {
    #             'Content-Disposition': content_disposition(filename)
    #         }
    #     }


    @api.constrains('subdiary','voucher_number')
    def validate_sequence_unique(self):
        for rec in self:
            if rec.subdiary and rec.voucher_number:
                duplicated_records = self.env['documental.settlements.detail'].search([
                    ('subdiary','=',rec.subdiary),
                    ('voucher_number','=',rec.voucher_number),
                    ('id','!=', rec.id),
                ])
                if duplicated_records:
                    raise ValidationError( _('The voucher number %s is repeated for the %s subdiary') % ( rec.voucher_number,rec.subdiary ) )


    # def button_god(self):
    #     dsd_ids = self.env['documental.settlements.detail'].search([('state','in',('waiting_administration_validation','to_settle','settled'))])
    #     _logger.info("\n\n\n dsd_ids: %s \n\n\n", dsd_ids)
    #     _logger.info("\n\n\n len(dsd_ids): %s \n\n\n", len(dsd_ids))
    #     for line in dsd_ids:
    #         line.button_main_gloss()
    #         line.button_conversion()
    #         line.button_change_type()
    #         line.fill_data()


    def button_main_gloss(self):
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


    def button_conversion(self):
        for rec in self:
            rec.conversion_type = 'V'
            rec.flag_currency_conversion = 'S'


    @api.onchange('exchange_type_date')
    def _onchange_change_type(self):
        for rec in self:
            change_type = self.env['change.type'].search([('date','=',rec.exchange_type_date)]).mapped('sell')
            if len(change_type) == 0:
                rec.change_type = 0.00
            else:
                rec.change_type = change_type[0]


    def fill_data(self):
        values_igv = {}
        values_detraction_in = {}
        values_detraction_out = {}
        values_to_pay = {}
        values_base_amount = {}
        values_surcharge = {}
        total_igv = 0.00
        total_base_amount = 0.00
        total_surcharge = 0.00
        service_code = ''
        percentage = 0.00
        self.journal_ids = [(5,0,0)]
        for line in self.settlement_detail_line_ids:
            if line.igv_tax not in ('consumption_surcharge','exonerated'):
                total_igv += line.igv
        for line in self.settlement_detail_line_ids:
            if line.igv_tax != 'consumption_surcharge':
                total_base_amount += line.base_amount
        for line in self.settlement_detail_line_ids:
            if line.igv_tax == 'consumption_surcharge':
                total_surcharge += line.base_amount
        service_list = [line.service_type_id.code for line in self.settlement_detail_line_ids]
        _logger.info("\n\n\n service_list: %s \n\n\n", service_list)
        if False not in service_list:
            service_code = ','.join(service_list)
        else:
            service_code = ''
        percentage_list = [line.service_type_id.percentage for line in self.settlement_detail_line_ids]
        if False not in percentage_list:
            percentage = percentage_list[0]
        else:
            percentage = 0.00

        values_to_pay.update({
            'name': _('Total amount'),
            'account_id': self.env['account.account'].search([('code','=','421201')]).id if self.currency == 'soles' else self.env['account.account'].search([('code','=','421202')]).id,
            'debit': 0.00,
            'credit': self.to_pay + self.detraction_amount,  # FIRST CREDIT
            'annex_code': self.ruc,
            'document_number': self.document,
        })
        values_detraction_in.update({
            'name': _('Detraction'),
            'account_id': self.env['account.account'].search([('code','=','421203')]).id,
            'debit': 0.00,
            'credit': self.detraction_amount,   # SECOND CREDIT
            'rate_type': service_code,
            'annex_code': self.ruc,
            'document_number': self.document,
            'detraction_retention_type': percentage,
            'soles_detraction_perception_amount': self.to_pay + self.detraction_amount,
            'reference_document_type': self.document_type_code,
            'reference_document_number': self.document,
            'reference_document_date': self.date,
        })
        values_igv.update({
            'name': 'IGV',
            'account_id': self.env['account.account'].search([('code','=','401111')]).id,
            'debit': total_igv, # FIRST DEBIT
            'credit': 0.00,
            'annex_code': False,
            'document_number': self.document,
        })
        values_detraction_out.update({
            'name': _('Detraction'),
            'account_id': self.env['account.account'].search([('code','=','421201')]).id if self.currency == 'soles' else self.env['account.account'].search([('code','=','421202')]).id,
            'debit': self.detraction_amount,    # SECOND DEBIT
            'credit': 0.00,
            'annex_code': self.ruc,
            'document_number': self.document,
        })
        values_base_amount.update({
            'name': _('Amount Base'),
            'account_id': False,
            'cost_center_id': self.cost_center_id.id,
            # 'debit': total_base_amount - self.detraction_amount, # THIRD DEBIT
            'debit': total_base_amount, # THIRD DEBIT
            'credit': 0.00,
            'annex_code': self.ruc,
            'document_number': self.document,
        })
        values_surcharge.update({
            'name': _('Consumption surcharge'),
            'account_id': False,
            'cost_center_id': self.cost_center_id.id,
            'debit': total_surcharge,   # FOURTH DEBIT
            'credit': 0.00,
            'annex_code': self.ruc,
            'document_number': self.document,
        })
        if self.to_pay > 0.00:
            self.journal_ids = [(0,0,values_to_pay)]
        if self.detraction_amount > 0.00:
            self.journal_ids = [(0,0,values_detraction_in)]
        if total_igv > 0.00:
            self.journal_ids = [(0,0,values_igv)]
        if self.detraction_amount > 0.00:
            self.journal_ids = [(0,0,values_detraction_out)]
        if total_base_amount - self.detraction_amount:
            self.journal_ids = [(0,0,values_base_amount)]
        if total_surcharge > 0.00:
            self.journal_ids = [(0,0,values_surcharge)]


    def attach_in_chatter(self):
        attachments = []
        for rec in self:
            if rec.document_file:
                attach = {
                    'name':rec.document_filename,
                    'datas':rec.document_file,
                    'store_fname':rec.document_filename,
                    'res_model':rec._name,
                    'res_id':rec.id,
                    'type':'binary',
                }
                attachment = self.env['ir.attachment'].create(attach)
                attachments.append(attachment.id)
                # rec.message_post(
                #     body=_("Document file: %s") % (rec.document_filename),
                #     attachment_ids=[self.env['ir.attachment'].create(attach).id],
                # )


    # def attach_in_chatter(self):
    #     attachments = []
    #     for line in self.settlement_detail_ids:
    #         if line.document_file:
    #             attach = {
    #                 'name': line.document_filename,
    #                 'datas': line.document_file,
    #                 'store_fname': line.document_filename,
    #                 'res_model': self._name,
    #                 'res_id': self.id,
    #                 'type': 'binary',
    #             }
    #             attachment = self.env['ir.attachment'].create(attach)
    #             attachments.append(attachment.id)


    @api.depends('ruc','document')
    def compute_filename(self):
        for rec in self:
            if rec.document_file:
                if rec.ruc and rec.document:
                    rec.document_filename = rec.ruc + '-' + rec.document


    @api.depends('settlement_detail_line_ids')
    def _compute_amount_detraction_to_pay_igv_base(self):
        for rec in self:
            to_pay = 0.00
            detraction = 0.00
            if rec.settlement_detail_line_ids:
                rec.amount = sum(rec.settlement_detail_line_ids.mapped('amount'))
                rec.igv_total = sum(rec.settlement_detail_line_ids.mapped('igv'))
                rec.base_amount_total = sum(rec.settlement_detail_line_ids.mapped('base_amount'))
            else:
                rec.amount = 0.00
                rec.igv_total = 0.00
                rec.base_amount_total = 0.00
                rec.retention_amount = 0.00
                rec.detraction_amount = 0.00
                rec.to_pay = 0.00
            if rec.documental_settlement_id.requirement_id.amount_currency_type == 'soles':
                if rec.is_taxable:
                    if rec.settlement_detail_line_ids:
                        max_amount_line = rec.env['settlement.detail.line'].search([('settlement_detail','=',rec.id)], order='amount desc', limit=1)
                        total_amount = sum(rec.settlement_detail_line_ids.mapped('amount'))
                        if total_amount > max_amount_line.service_type_id.amount_from:
                            if max_amount_line.service_type_id.detraction == True:
                                rec.detraction_amount = round((max_amount_line.service_type_id.percentage * total_amount) / 100, 0)
                                rec.to_pay = total_amount - round((max_amount_line.service_type_id.percentage * total_amount) / 100, 0)
                                rec.retention_amount = 0.00
                            elif max_amount_line.service_type_id.retention == True:
                                rec.retention_amount = ( max_amount_line.service_type_id.percentage * total_amount ) / 100
                                rec.to_pay = total_amount - ( max_amount_line.service_type_id.percentage * total_amount ) / 100
                                rec.detraction_amount = 0.00
                            else:
                                rec.retention_amount = 0
                                rec.detraction_amount = 0
                                rec.to_pay = total_amount
                        else:
                            rec.retention_amount = 0.00
                            rec.detraction_amount = 0.00
                            rec.to_pay = total_amount
                else:
                    rec.to_pay = sum(rec.settlement_detail_line_ids.mapped('amount'))
                    rec.detraction_amount = 0.00
                    rec.retention_amount = 0.00
            if rec.documental_settlement_id.requirement_id.amount_currency_type == 'dolares':
                if rec.is_taxable:
                    if rec.settlement_detail_line_ids:
                        max_amount_line = rec.env['settlement.detail.line'].search([('settlement_detail','=',rec.id)], order='amount desc', limit=1)
                        total_amount = sum(rec.settlement_detail_line_ids.mapped('amount'))
                        sale_change_type = self.env['change.type'].search([('date','=',rec.date)]).mapped('sell')
                        if len(sale_change_type) == 0:
                            change_type = 0.00
                        else:
                            change_type = sale_change_type[0]
                        if total_amount * change_type > max_amount_line.service_type_id.amount_from:
                            if max_amount_line.service_type_id.detraction == True:
                                rec.detraction_amount = round((max_amount_line.service_type_id.percentage * total_amount) / 100, 0)
                                rec.to_pay = total_amount - round((max_amount_line.service_type_id.percentage * total_amount) / 100, 0)
                                rec.retention_amount = 0.00
                            elif max_amount_line.service_type_id.retention == True:
                                rec.retention_amount = ( max_amount_line.service_type_id.percentage * total_amount ) / 100
                                rec.to_pay = total_amount - ( max_amount_line.service_type_id.percentage * total_amount ) / 100
                                rec.detraction_amount = 0.00
                            else:
                                rec.retention_amount = 0
                                rec.detraction_amount = 0
                                rec.to_pay = total_amount
                        else:
                            rec.retention_amount = 0.00
                            rec.detraction_amount = 0.00
                            rec.to_pay = total_amount
                else:
                    rec.to_pay = sum(rec.settlement_detail_line_ids.mapped('amount'))
                    rec.detraction_amount = 0.00
                    rec.retention_amount = 0.00


    @api.onchange('is_taxable','igv_included','settlement_detail_line_ids')
    def _onchange_tax_igv(self):
        if self.is_taxable == False:
            self.igv_included = False
        if self.igv_included == True:
            self.is_taxable = True


    @api.onchange('ruc')
    def onchange_partner_ruc(self):
        if self.ruc:
            ruc = self.ruc
            partner = self.env['res.partner'].search([('vat','=',ruc)]).name
            if partner:
                self.partner = partner
            if len(ruc) == 11:
                partner = self.env['res.partner'].search([('vat','=',ruc)]).name
                if partner:
                    self.partner = partner
                else:
                    # info = ConsultarRUC(ruc)[0][0]
                    name = apiperu_ruc(self.ruc)[3]
                    self.partner = name
                    # self.partner = info[0].split('-')[-1].strip() if 'PERSONA' not in info[1] else info[2].split('-')[-1].strip()
        else:
            self.partner = False


    @api.model
    def _get_file_name(self, vals):
        return vals.get('document_filename') or _('File')
    

    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref('mkt_documental_managment.view_settlement_detail_form')
        return {
            'name': _('Settlement Detail Lines'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'documental.settlements.detail',
            'views': [(view.id, 'form')],
            'res_id': self.id,
            'target': 'new',
        }


class SettlementsDetailLine(models.Model):
    _name = 'settlement.detail.line'
    _description = 'settlement detail line'

    settlement_id = fields.Many2one(comodel_name='settlement', string='Settlement')
    name = fields.Char(string="Description")
    settlement_detail = fields.Many2one(comodel_name="documental.settlements.detail", string="Settlement Detail")
    account_id = fields.Many2one(comodel_name="account.account", string="Account")
    debit = fields.Float(string="Debit", default=0.0, digits=(10,2))
    credit = fields.Float(string="Credit", default=0.0, digits=(10,2))
    service_type_id = fields.Many2one(comodel_name="requirement.service.type", string="Service Type")
    igv_tax = fields.Selection(string="Tax",
                               selection=[('levied','Levied'),
                                          ('exonerated','Exonerated'),
                                          ('consumption_surcharge','Consumption Surcharge')],
                               default='levied')
    tax_igv_id = fields.Many2one(comodel_name="tax.taxes", string="% IGV", related="settlement_detail.tax_igv_id", store=True)
    igv_included = fields.Boolean(string="IGV Included?", related="settlement_detail.igv_included")
    quantity = fields.Integer(string="Quantity", digits=(10, 2))
    unit_price = fields.Float(string="Unit Price", digits=(10, 3))
    base_amount = fields.Float(string="Base Amount", compute="_compute_base_igv_amount", digits=(10, 2), store=True)
    igv = fields.Float(string="IGV", compute="_compute_base_igv_amount", digits=(10, 2), store=True)
    amount = fields.Float(string="Amount", compute="_compute_base_igv_amount", digits=(10, 2), store=True)


    @api.depends('quantity', 'unit_price', 'igv_included', 'igv_tax', 'tax_igv_id')
    def _compute_base_igv_amount(self):
        for rec in self:
            if rec.settlement_detail.igv_included == True:
                if rec.igv_tax == 'levied':
                    rec.base_amount = ( rec.quantity * rec.unit_price ) / ( 1 + ( rec.tax_igv_id.percentage / 100 ) )
                    rec.igv = ( ( rec.quantity * rec.unit_price ) / ( 1 + ( rec.tax_igv_id.percentage / 100 ) ) ) * (rec.tax_igv_id.percentage / 100)
                    rec.amount = rec.quantity * rec.unit_price
                if rec.igv_tax in ('exonerated','consumption_surcharge'):
                        rec.base_amount = rec.quantity * rec.unit_price
                        rec.igv = 0.00
                        rec.amount = rec.quantity * rec.unit_price
            else:
                if rec.igv_tax == 'levied':
                    rec.base_amount = rec.quantity * rec.unit_price
                    rec.igv = ( rec.quantity * rec.unit_price ) * ( rec.tax_igv_id.percentage / 100 )
                    rec.amount = ( rec.quantity * rec.unit_price ) + ( ( rec.quantity * rec.unit_price ) * ( rec.tax_igv_id.percentage / 100 ) )
                if rec.igv_tax in ('exonerated','consumption_surcharge'):
                    rec.base_amount = rec.quantity * rec.unit_price
                    rec.igv = 0.00
                    rec.amount = rec.quantity * rec.unit_price


class SettlementLineType(models.Model):
    _name = 'settlement.line.type'
    _description = 'Settlement Line Type'

    name = fields.Char(string="Document Type")
    budgetable = fields.Selection(string="Budgetable", selection=[('yes','Yes'),('no','No')])
    national_format = fields.Boolean(string="National Format", default=False)
    short_name = fields.Char(string="Short name")
    is_ruc = fields.Boolean(string="Is RUC", default=True)
    accountable = fields.Boolean(string="Accountable", default=False)
    is_return = fields.Boolean(default=False, string='Is return')
    is_reimbursement = fields.Boolean(default=False, string='Is reimbursement')
    proof_purchase = fields.Boolean(default=False, string='Proof of purchase')
    visible_in_requirement = fields.Boolean(string="Visible in Requirement", default=True)
    visible_in_liquidation = fields.Boolean(string="Visible in Liquidation", default=True)