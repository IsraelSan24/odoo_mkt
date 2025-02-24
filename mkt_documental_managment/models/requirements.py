from odoo import _, api, fields, models
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from odoo.addons.mkt_documental_managment.models.api_ruc import apiperu_ruc
from odoo.addons.mkt_documental_managment.models.signature import signature_generator
from odoo.addons.mkt_documental_managment.models.number_to_string import number_to_string
import io
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import base64
import logging
_logger = logging.getLogger(__name__)


state = [
    ('draft', 'Draft'),
    ('waiting_boss_validation', 'Waiting Boss Validation'),
    ('waiting_budget_executive_validation', 'Waiting Budget Executive Validation'),
    ('waiting_intern_control_validation', 'Waiting Intern Control Validation'),
    ('waiting_administration_validation', 'Waiting Administration Validation'),
    ('to_settle', 'To Settle'),
    ('settled', 'Settled'),
    ('refused', 'Refused'),
]

urgency_status = [
    ('0','Normal'),
    ('1','Urgent'),
]


states = [
    ('draft', 'Draft'),
    ('executive', 'Executive'),
    ('responsible', 'Responsible'),
    ('intern_control', 'Intern Control'),
    ('administration', 'Administration'),
    ('to_settle', 'To Settle'),
    ('settled', 'Settled'),
    ('refused', 'Refused'),
]

months = [('january', 'Enero'), ('february', 'Febrero'), ('march', 'Marzo'),
          ('april', 'Abril'), ('may', 'Mayo'),
          ('june', 'Junio'),('july', 'Julio'),('august', 'Agosto'),
          ('september', 'Septiembre'),('octuber', 'Octubre'),
          ('november', 'Noviembre'),('december', 'Diciembre')
]

currency_type = [
    ('soles', 'Soles'),
    ('dolares', 'Dólares'),
]


def get_default_igv(self):
    return self.env['tax.taxes'].search([('name','=','IGV(18%)')]).id


def get_default_fullname(self):
    full_name = self.env.user.id
    return full_name


def get_default_dni(self):
    vat = self.env.user.vat
    return vat


class DocumentalRequirements(models.Model):
    _name = 'documental.requirements'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Documental Requirements'
    _order = 'id desc'

    name = fields.Char(copy=False, default=lambda self: _('New'), required=True, string="RQ Number")
    unify = fields.Boolean(default=True, string='Unify')
    state = fields.Selection(string='State', selection=state, default='draft', tracking=True)
    timer_state = fields.Selection([
        ('on_time','On time'),
        ('late','Late')], string='Timer',
        copy=False, default='on_time', required=True)
    start_time = fields.Datetime(string='Start time')
    urgency = fields.Selection(selection=urgency_status, default='0', string='Urgency')
    group_administration = fields.Boolean(compute='_compute_administrastion_group', default=False, string='is administrator')
    paid_to = fields.Many2one(comodel_name='res.partner', string='Paid to')
    bank = fields.Many2one(comodel_name="res.bank", string="Bank", domain="[('id','in',current_partner_bank_ids)]")
    current_partner_bank_ids = fields.Many2many(comodel_name='res.bank', compute='_compute_bank')
    customer_account_number = fields.Char(string='Customer Bank Account Number', tracking=True)
    dni_or_ruc = fields.Char(string='DNI or RUC', tracking=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", default=lambda self: self.env.user.employee_id)
    department_id = fields.Many2one(related='employee_id.department_id', string='Department', store=True)
    refund_employee_id = fields.Many2one(comodel_name="hr.employee", string="Refund employee")
    card_payment = fields.Boolean(string="Payment with Card", default=False)

    accounting_account = fields.Char(copy=False, string="accounting account", store=True)

    partner_id = fields.Many2one(comodel_name="res.partner", related='budget_id.partner_id', string='Customer')
    partner_bool = fields.Boolean(string="Partner Bool", default=False)
    campaign_id = fields.Many2one(comodel_name="budget.campaign", related='budget_id.campaign_id', string='Activity')
    campaign_bool = fields.Boolean(string="Activity", default=False)
    amount_char = fields.Char(string='For the Sum of', tracking=True)

    budget_id = fields.Many2one(comodel_name="budget", string="PPTO Number", domain="[('state','=','active')]")
    budget_track = fields.Char(string="Budget", compute="compute_track_field", store=True, tracking=True)
    cost_center_id = fields.Many2one(comodel_name="cost.center", related='budget_id.cost_center_id', string='CC Number')
    cost_center_bool = fields.Boolean(string="Cost center bool", default=False)
    year_month_id = fields.Many2one(comodel_name="year.month", related='budget_id.year_month_id', string="Month/Year")
    year_month_bool = fields.Boolean(string="Month/year bool", default=False)
    show_budget_detail = fields.Boolean(default=False, string='Show budget detail')

    amount_currency_type = fields.Selection(string='Currency type', selection=currency_type, default='soles', tracking=True)
    currency_id = fields.Many2one(comodel_name='res.currency')

    check_or_operation = fields.Selection(string="Check/Operation", selection=[('check','Check'),('operation','Operation')], default='operation', copy=False, tracking=True)
    check_number = fields.Char(string='Check Number', copy=False, tracking=True)
    operation_number = fields.Char(string='Operation Number', copy=False, tracking=True)
    payment_date = fields.Date(string="Payment Date", copy=False, tracking=True)
    payment_bank_id = fields.Many2one(comodel_name='res.bank', string='Bank')

    concept = fields.Char(string='Concept', tracking=True)
    type = fields.Selection(string="Type", selection=[('service','Service'),('property','Property')])
    deduction_bank = fields.Many2one(comodel_name="res.bank", related="paid_to.deduction_bank", string="Bank", store=True)
    deduction_acc_number = fields.Char(string="Account Number", related="paid_to.deduction_acc_number", store=True)

    document_id = fields.Many2one(comodel_name="documental.requirements")
    full_name = fields.Many2one(comodel_name="res.users", string='Full Name', default=get_default_fullname)
    dni = fields.Char(string='DNI', default=get_default_dni, tracking=True)
    date = fields.Datetime(string='Date', default=fields.Datetime.now, tracking=True)
    detail = fields.Char(string='Detail', tracking=True)

    settlement_id = fields.Many2one(comodel_name="documental.settlements", copy=False)
    
    in_bank = fields.Boolean(default=False, copy=False, tracking=True)
    requirement_payroll_id = fields.Many2one(comodel_name="requirement.payroll", string="Payroll")
    transfer_id = fields.Many2one(comodel_name="report.administration", string="Transfer")
    active = fields.Boolean(string='Active', default=True, tracking=True)

    detraction_amount = fields.Float(string="Amount Detraction", compute='_compute_detraction_to_pay', store=True)
    detraction_amount_char = fields.Char(string="For the sum of", compute="_compute_detraction_to_pay", tracking=True, store=True)
    retention_amount = fields.Float(string="Amount Retention", compute="_compute_detraction_to_pay", tracking=True, store=True)
    to_pay_supplier = fields.Float(string="Pay to Supplier", compute="_compute_detraction_to_pay", store=True)
    total_vendor = fields.Float(compute='_compute_settlement_vendor', string='To pay', store=True)
    total_vendor_text = fields.Char(compute='_compute_total_vendor_text', string='To pay in text')
    total_detraction = fields.Float(compute='_compute_total_detraction', string='Detraction', store=True)
    total_detraction_text = fields.Char(compute='_compute_total_detraction_text', string='Detraction in text')
    total_retention = fields.Float(compute='_compute_total_retention', string='Retention', store=True)
    total_retention_text = fields.Char(compute='_compute_total_retention_text', string='Retention in text')
    is_ruc = fields.Boolean(string="Is RUC")

    requirement_detail_justification_ids = fields.One2many('requirement.detail.justification', 'requirement_id', string="Requirement Detail Justification")
    restricted_requirement_detail_justification_ids = fields.One2many('requirement.detail.justification', 'requirement_id', string="Requirement Detail Justification")

    is_refund = fields.Boolean(default=False, copy=False)
    refund_user_id = fields.Many2one(comodel_name="res.users", copy=False)
    refund_requirement_id = fields.Many2one(comodel_name='documental.requirements', string='Origin', copy=False)
    account_check = fields.Boolean(default=False, copy=False, string='Account check')
    repeated = fields.Boolean(default=False, string='Repeated')
    repeated_document = fields.Char(string='Repeated documents')

    balance = fields.Float(compute='_compute_balance', string='Balance', store=True)
    
    current_user = fields.Char(compute='_compute_current_user', string='Current user')
    is_current_executive = fields.Boolean(compute='_compute_is_current_budget', default=False, string='Is budget executive?')
    
    total_paid = fields.Float(compute='_compute_total_paid', string='Total paid')
    pending_to_pay = fields.Float(compute='_compute_pending_to_pay', string='Pending to pay')
    requirement_payment_ids = fields.One2many('requirement.payment', 'requirement_id', string='Payments')

    #* Settlement
    settlement_total_lines = fields.Integer(compute='_compute_settlement_total_lines', string='Settlement total lines', store=True)
    settlement_amount = fields.Float(compute='_compute_settlement_amount', string='Settlement amount total', store=True)

    settlement_ids = fields.One2many('settlement', 'requirement_id', string='Settlement')
    lock_settlement_ids = fields.One2many('settlement', 'requirement_id', string='Lock settlement')

    settlement_state = fields.Selection(selection=states, default='draft', string='Settlement state', tracking=True, copy=False)
    settlement_repeated_document = fields.Char(default=False, string='Repeated settlement document')

    #* Requirement
    amount_soles = fields.Monetary(string='Amount(S/.)', currency_field='currency_id', compute="_compute_amount_soles_uss", store=True)
    amount_uss = fields.Monetary(string='Amount(USS)', currency_field='currency_id', compute="_compute_amount_soles_uss", store=True )

    requirement_detail_ids = fields.One2many('requirement.detail', 'requirement_id', string="Requirement Detail")
    restricted_requirement_detail_ids = fields.One2many('requirement.detail', 'requirement_id', string="Requirement Detail")

    requirement_state = fields.Selection(selection=states, default='draft', string='Requirement state', tracking=True)
    report_administration_id = fields.Many2one(comodel_name='report.administration', copy=False)

    #* Requirement signature fields
    petitioner_signature = fields.Binary(string="Petitioner", copy=False, attachment=True)
    is_petitioner_signed = fields.Boolean(default=False, copy=False, tracking=True)
    petitioner_signed_on = fields.Datetime(string="Petitioner signed on", copy=False, tracking=True)
    user_petitioner_signed_id = fields.Many2one(comodel_name='res.users', copy=False, string='User petitioner signed')

    boss_signature = fields.Binary(string="Executive", copy=False, attachment=True)
    is_boss_signed = fields.Boolean(default=False, copy=False, tracking=True)
    boss_signed_on = fields.Datetime(string="Boss signed on", copy=False, tracking=True)
    user_boss_signed_id = fields.Many2one(comodel_name='res.users', copy=False, string='User boss signed')

    budget_executive_signature = fields.Binary(string="Budget Executive", copy=False, attachment=True)
    is_budget_executive_signed = fields.Boolean(default=False, copy=False, tracking=True)
    budget_executive_signed_on = fields.Datetime(string="Budget executive signed on", copy=False, tracking=True)
    user_budget_executive_signed_id = fields.Many2one(comodel_name='res.users', copy=False, string='User executive signed')

    intern_control_received = fields.Datetime(string='Intern control reception')

    intern_control_signature = fields.Binary(string="Intern Control", copy=False, attachment=True)
    is_intern_control_signed = fields.Boolean(default=False, copy=False, tracking=True)
    intern_control_signed_on = fields.Datetime(string="Intern control signed on", copy=False, tracking=True)
    user_intern_control_signed_id = fields.Many2one(comodel_name='res.users', copy=False, string='User intern control signed')

    administration_signature = fields.Binary(string="Administration", copy=False, attachment=True)
    is_administration_signed = fields.Boolean(default=False, copy=False, tracking=True)
    administration_signed_on = fields.Datetime(string="Administration signed on", copy=False, tracking=True)
    user_administration_signed_id = fields.Many2one(comodel_name='res.users', copy=False, string='User administration signed')


    #* Settlement signature fields
    settlement_petitioner_signature = fields.Binary(string='Petitioner', copy=False, attachment=True)
    settlement_petitioner_signed_on = fields.Datetime(string='Settlement petitioner signed on', copy=False, tracking=True)
    settlement_petitioner_user_id = fields.Many2one(comodel_name='res.users', copy=False, string='Settlement petitioner signed by')

    settlement_boss_signature = fields.Binary(string='Executive', copy=False, attachment=True)
    settlement_boss_signed_on = fields.Datetime(string='Settlement boss signed on', copy=False, tracking=True)
    settlement_boss_user_id = fields.Many2one(comodel_name='res.users', copy=False, string='Settlement boss signed by')

    settlement_budget_executive_signature = fields.Binary(string='Budget executive', copy=False, attachment=True)
    settlement_budget_executive_signed_on = fields.Datetime(string='Settlement budget executive signed on', copy=False, tracking=True)
    settlement_budget_executive_user_id = fields.Many2one(comodel_name='res.users', copy=False, string='Settlement budget executive signed by')

    settlement_intern_control_received = fields.Datetime(string='Settlement intern control received')

    settlement_intern_control_signature = fields.Binary(string='Intern control', copy=False, attachment=True)
    settlement_intern_control_signed_on = fields.Datetime(string='Settlement intern contrnol signed on', copy=False, tracking=True)
    settlement_intern_control_user_id = fields.Many2one(comodel_name='res.users', copy=False, string='Settlement intern control signed by')

    settlement_administration_signature = fields.Binary(string='Administration', copy=False, attachment=True)
    settlement_administration_signed_on = fields.Datetime(string='Settlement administration signed on', copy=False, tracking=True)
    settlement_administration_user_id = fields.Many2one(comodel_name='res.users', copy=False, string='Settlement administration signed by')


    @api.depends('total_paid',
                 'amount_uss',
                 'amount_soles',
                 'settlement_ids',
                 'requirement_detail_ids',
                 'requirement_payment_ids')
    def _compute_pending_to_pay(self):
        for rec in self:
            # amount_total = rec.amount_soles if rec.amount_soles > 0 else rec.amount_uss
            rec.pending_to_pay = rec.total_vendor - rec.total_paid


    @api.depends('amount_uss',
                 'amount_soles',
                 'settlement_ids',
                 'requirement_detail_ids',
                 'requirement_payment_ids')
    def _compute_total_paid(self):
        for rec in self:
            rec.total_paid = sum(rec.requirement_payment_ids.mapped('amount'))


    def update_payment_lines(self):
        for rec in self:
            if rec.requirement_state in ('to_settle','settled') and rec.payment_date:
                _logger.info('\n\n\n rec.id: %s \n\n\n', rec.id)
                self.env['requirement.payment'].create({
                    'requirement_id': rec.id,
                    'check_or_operation': rec.check_or_operation,
                    'payment_date': rec.payment_date,
                    'operation_number': rec.operation_number,
                    'requirement_payroll_id': rec.requirement_payroll_id.id,
                    # 'amount': rec.amount_soles if rec.amount_soles > 0 else rec.amount_uss,
                    'amount': rec.total_vendor,
                })


    def _compute_is_current_budget(self):
        if self.current_user == self.budget_id.executive_id.name:
            self.is_current_executive = True
        else:
            self.is_current_executive = False


    def _compute_current_user(self):
        for rec in self:
            rec.current_user = self.env.user.name


    def validation_vouchers(self):
        for rec in self.settlement_ids:
            rec.validation_voucher()


    @api.onchange('settlement_ids')
    def _onchange_repeated_settlement_document(self):
        text = []
        for rec in self.settlement_ids:
            settlements = self.env['settlement'].sudo().search([('dni_ruc','=',rec.dni_ruc),('document_type_id','=',rec.document_type_id.id),('document','=',rec.document),('requirement_id.active','=',True)]).mapped('requirement_id.name')
            if self.name in settlements:
                settlements.remove(self.name)
            if len(settlements) != 0 and rec.document_type_id and rec.document:
                string_text = 'The %s %s is repeated on %s' % ( rec.document_type_id.name, rec.document, ', '.join(settlements) )
                text.append(string_text)
        self.settlement_repeated_document = '. '.join(text)


    def compute_retention_vendor(self):
        records = self.env['settlement'].sudo().search([('retention','!=',0)])
        for rec in records:
            rec.compute_detraction_retention()


    # * Onchange methods
    @api.onchange('amount_currency_type')
    def _onchange_currency(self):
        if self.amount_currency_type == 'soles':
            soles = self.env['res.currency'].search([('name','=','PEN')])
            self.currency_id = soles.id
        if self.amount_currency_type == 'dolares':
            dolares = self.env['res.currency'].search([('name','=','USD')])
            self.currency_id = dolares.id


    @api.onchange('requirement_detail_ids')
    def _onchange_repeated_requirement_document(self):
        text = []
        for rec in self.requirement_detail_ids:
            requirements = self.env['requirement.detail'].sudo().search([('ruc','=',rec.ruc),('document_type','=',rec.document_type.id),('document','=',rec.document),('requirement_id.active','=',True)]).mapped('requirement_id.name')
            if self.name in requirements:
                requirements.remove(self.name)
            if len(requirements) != 0 and rec.document_type and rec.document:
                string_text = 'The %s %s is repeated on %s' % ( rec.document_type.name, rec.document, ', '.join(requirements) )
                text.append(string_text)
        self.repeated_document = '. '.join(text)


    # @api.onchange('requirement_detail_ids')
    # def _onchange_repeated_document(self):
    #     text = ""
    #     for rec in self.requirement_detail_ids:
    #         # rqs = self.env['requirement.detail'].search([('ruc','=',rec.ruc),('document_type','=',rec.document_type),('document','=',rec.document)]).mapped('requirement_id.name')
    #         rqs = self.env['requirement.detail'].sudo().search([('ruc','=',rec.ruc),('document_type','=',rec.document_type.id),('document','=',rec.document)]).mapped('requirement_id.name')
    #         _logger.info('\n\n\n rqs: %s \n\n\n', rqs)
    #         if self.name in rqs:
    #             rqs.remove(self.name)
    #         _logger.info('\n\n\n rqs remove: %s \n\n\n', rqs)
    #         if rec.repeated:
    #             text += _('The %s %s is repeated on %s. \n') % (
    #                 rec.document_type.name,
    #                 rec.document,
    #                 ', '.join(rqs)
    #             )
    #     self.repeated_document = text
    #     if len(self.repeated_document) != 0:
    #         self.repeated = True
    #     else:
    #         self.repeated = False


    @api.onchange('paid_to')
    def onchange_dni(self):
        for rec in self:
            if rec.paid_to:
                rec.dni_or_ruc = rec.paid_to.vat
                if rec.paid_to.vat:
                    if len(rec.paid_to.vat) == 11:
                        rec.is_ruc = True
                    if len(rec.paid_to.vat) == 8:
                        rec.is_ruc = False
            else:
                rec.dni_or_ruc = False
                rec.bank = False
                rec.customer_account_number = False

            if rec.dni_or_ruc and rec.paid_to:
                if len(rec.dni_or_ruc) == 8:
                    if rec.paid_to.spreadsheet == 'mkt_spreadsheet' and rec.paid_to.province_id.name == 'Lima':
                        rec.accounting_account = '141301'
                    elif rec.paid_to.spreadsheet == 'mkt_spreadsheet' and rec.paid_to.province_id.name != 'Lima':
                        rec.accounting_account = '141303'
                    elif rec.paid_to.spreadsheet == 'sp_spreadsheet':
                        rec.accounting_account = '162904'
                    else:
                        rec.accounting_account = ''
                elif len(rec.dni_or_ruc) == 11:
                    if rec.unify == True:
                        if rec.amount_currency_type == 'soles':
                            rec.accounting_account = '422101'
                        elif rec.amount_currency_type == 'dolares':
                            rec.accounting_account = '422102'
                        else:
                            rec.accounting_account = ''
                    else:
                        if rec.amount_currency_type == 'soles':
                            rec.accounting_account = '421201 '
                        elif rec.amount_currency_type == 'dolares':
                            rec.accounting_account = '421202'
                        else:
                            rec.accounting_account = ''
                else:
                    rec.accounting_account = ''


    @api.onchange('amount_currency_type')
    def onchange_amount(self):
        if self.amount_currency_type == 'soles':
            self.amount_uss = 0
        if self.amount_currency_type == 'dolares':
            self.amount_soles = 0


    @api.onchange('check_or_operation')
    def onchange_check_operation(self):
        if self.check_or_operation == 'check':
            self.operation_number = False
        if self.check_or_operation == 'operation':
            self.check_number = False


    @api.onchange('amount_soles','amount_uss','requirement_detail_ids')
    def onchange_amount_char(self):
        soles = 0
        uss = 0
        if self.amount_soles:
            if self.amount_soles > 0 and self.amount_soles < 1000000000000:
                soles = number_to_string(self.amount_soles)
                self.amount_char = (soles.replace("uno mil", "un mil") + " soles").upper()
        if self.amount_uss:
            if self.amount_uss > 0 and self.amount_uss < 1000000000000:
                uss = number_to_string(self.amount_uss)
                self.amount_char = (uss.replace("uno mil", "un mil") + " dólares").upper()
            if self.amount_uss == 0.00:
                self.amount_char = 'CERO CON 00/100 DÓLARES'


    @api.onchange('bank','card_payment')
    def onchange_acc_number(self):
        if self.card_payment == False:
            if self.bank:
                partner_bank = self.env['res.partner.bank'].search([('partner_id','=',self.paid_to.id),('bank_id','=',self.bank.id)])
                if partner_bank:
                    self.customer_account_number = partner_bank.acc_number
            else:
                self.customer_account_number = False
        else:
            self.customer_account_number = False


    # * Compute methods
    @api.depends('settlement_ids')
    def _compute_settlement_total_lines(self):
        for rec in self:
            rec.settlement_total_lines = len(rec.settlement_ids)


    @api.depends(
        'settlement_ids',
        'settlement_ids.settle_amount')
    def _compute_settlement_amount(self):
        for rec in self:
            not_return_lines = rec.settlement_ids.filtered(lambda line: not line.document_type_id.is_return)
            # rec.settlement_amount = round(sum( not_return_lines.mapped('settle_amount') ), 2)
            detraction_lines = rec.settlement_ids.filtered(lambda line: line.document_type_id.is_reimbursement)
            rec.settlement_amount = round(sum(not_return_lines.mapped('settle_amount')) - sum(detraction_lines.mapped('settle_amount')),2)


    @api.depends('amount_uss','amount_soles','settlement_amount','settlement_ids')
    def _compute_balance(self):
        for rec in self:
            requirement_amount = rec.amount_soles if rec.amount_soles != 0 else rec.amount_uss
            if rec.unify:
                not_return_lines = rec.settlement_ids.filtered(lambda line: not line.document_type_id.is_return)
                settlement_amount = sum( not_return_lines.mapped('settle_amount') )
                rec.balance = round( settlement_amount - requirement_amount, 2 )
            else:
                if rec.amount_currency_type == 'soles':
                    rec.balance = round(  rec.settlement_amount - rec.amount_soles, 2 )
                if rec.amount_currency_type == 'dolares':
                    rec.balance = round( rec.settlement_amount - rec.amount_uss, 2 )


    @api.depends('paid_to')
    def _compute_bank(self):
        if self.paid_to:    
            bank_ids = self.env['res.bank'].search([('id','in',self.paid_to.bank_ids.bank_id.ids)]).ids
            self.current_partner_bank_ids = bank_ids
        else:
            self.current_partner_bank_ids = False


    def _compute_administrastion_group(self):
        administration_group = self.env.ref('mkt_documental_managment.documental_requirement_administration')
        current_user = self.env.user
        for rec in self:
            if administration_group.id in current_user.groups_id.ids:
                rec.group_administration = True
            else:
                rec.group_administration = False


    @api.depends('budget_id')
    def compute_track_field(self):
        """ _Summary_
            This function give a value to a budget_track field.
        """
        for rec in self:
            if rec.budget_id:
                rec.budget_track = rec.budget_id.name


    def compute_amount_soles_uss(self):
        for rec in self:
            requirement_amount = sum(rec.requirement_detail_ids.mapped('amount'))
            settlement_amount = sum(rec.settlement_ids.mapped('settle_amount'))
            if rec.amount_currency_type == 'soles':
                rec.amount_soles = settlement_amount if rec.unify else requirement_amount
                rec.amount_uss = False
            if rec.amount_currency_type == 'dolares':
                rec.amount_soles = False
                rec.amount_uss = settlement_amount if rec.unify else requirement_amount


    @api.depends('unify',
                 'requirement_detail_ids',
                 'requirement_detail_justification_ids',
                 'amount_currency_type',
                 'requirement_detail_ids.requirement_detail_line_ids',
                 'settlement_ids')
    def _compute_amount_soles_uss(self):
        for rec in self:
            requirement_amount = sum(rec.requirement_detail_ids.mapped('required_amount')) + sum(rec.requirement_detail_justification_ids.mapped('amount'))
            not_return_lines = rec.settlement_ids.filtered(lambda line: not line.document_type_id.is_return)
            settlement_amount = round(sum( not_return_lines.mapped('settle_amount') ), 2)
            if rec.amount_currency_type == 'soles':
                rec.amount_soles = settlement_amount if rec.unify else requirement_amount
                rec.amount_uss = False
            if rec.amount_currency_type == 'dolares':
                rec.amount_uss = settlement_amount if rec.unify else requirement_amount
                rec.amount_soles = False


    @api.depends('requirement_detail_ids','settlement_ids')
    def _compute_total_detraction(self):
        for rec in self:
            if rec.unify:
                rec.total_detraction = sum( rec.settlement_ids.mapped('detraction') )
            else:
                rec.total_detraction = sum( rec.requirement_detail_ids.mapped('detraction') )


    @api.depends('requirement_detail_ids','settlement_ids','amount_currency_type')
    def _compute_total_detraction_text(self):
        for rec in self:
            if rec.amount_currency_type == 'soles':
                rec.total_detraction_text = ( number_to_string(round(rec.total_detraction, 2)) + ' soles' ).upper()
            if rec.amount_currency_type == 'dolares':
                rec.total_detraction_text = ( number_to_string(round(rec.total_detraction, 2)) + ' dolares' ).upper()


    @api.depends('requirement_detail_ids','settlement_ids')
    def _compute_total_retention(self):
        for rec in self:
            if rec.unify:
                rec.total_retention = sum( rec.settlement_ids.mapped('retention') )
            else:
                rec.total_retention = sum( rec.requirement_detail_ids.mapped('retention') )


    @api.depends('requirement_detail_ids','settlement_ids','amount_currency_type')
    def _compute_total_retention_text(self):
        for rec in self:
            if rec.amount_currency_type == 'soles':
                rec.total_retention_text = ( number_to_string(round(rec.total_retention, 2)) + ' soles' ).upper()
            if rec.amount_currency_type == 'dolares':
                rec.total_retention_text = ( number_to_string(round(rec.total_retention, 2)) + 'dolares' ).upper()


    @api.depends('requirement_detail_ids','settlement_ids')
    def _compute_settlement_vendor(self):
        for rec in self:
            if rec.unify:
                rec.total_vendor = sum( rec.settlement_ids.mapped('vendor') )
            else:
                rec.total_vendor = sum( rec.requirement_detail_ids.mapped('to_pay') )
                if len(rec.requirement_detail_ids) == 0 and len(rec.requirement_detail_justification_ids) != 0:
                    rec.total_vendor = sum( rec.requirement_detail_justification_ids.mapped('amount') )


    @api.depends('requirement_detail_ids','amount_currency_type','settlement_ids')
    def _compute_total_vendor_text(self):
        for rec in self:
            if rec.amount_currency_type == 'soles':
                rec.total_vendor_text = ( number_to_string(round(rec.total_vendor, 2)) + ' soles').upper()
            if rec.amount_currency_type == 'dolares':
                rec.total_vendor_text = ( number_to_string(round(rec.total_vendor, 2)) + ' dolares').upper()


    @api.depends('requirement_detail_ids',
                 'requirement_detail_justification_ids',
                 'amount_currency_type',
                 'requirement_detail_ids.requirement_detail_line_ids',
                 'requirement_detail_ids.amount')
    def _compute_detraction_to_pay(self):
        for rec in self:
            rec.detraction_amount = sum(rec.requirement_detail_ids.mapped('detraction'))
            detraction = number_to_string(rec.detraction_amount)
            rec.retention_amount = sum(rec.requirement_detail_ids.mapped('retention'))
            if rec.amount_soles:
                rec.to_pay_supplier = rec.amount_soles - sum(rec.requirement_detail_ids.mapped('detraction')) - sum(rec.requirement_detail_ids.mapped('retention'))
                rec.detraction_amount_char = (detraction.replace("uno mil", "un mil") + " soles").upper()
                if rec.amount_soles >= 0 and rec.amount_soles < 1000000000000:
                    rec.amount_char = (number_to_string(round(rec.amount_soles,2)).replace("uno mil", "un mil") + " soles").upper()
            elif rec.amount_uss:
                rec.to_pay_supplier = rec.amount_uss - sum(rec.requirement_detail_ids.mapped('detraction')) - sum(rec.requirement_detail_ids.mapped('retention'))
                rec.detraction_amount_char = (detraction.replace("uno mil", "un mil") + " dólares").upper()
                if rec.amount_uss >= 0 and rec.amount_uss < 1000000000000:
                    rec.amount_char = (number_to_string(round(rec.amount_uss,2)).replace("uno mil", "un mil") + " dólares").upper()
            else:
                rec.to_pay_supplier = 0.00


    # * Actions
    def compute_settlement_total_lines(self):
        self._compute_settlement_total_lines()


    def download_attach_files(self):
        combined_pdf_writer = PyPDF2.PdfFileWriter()
        for rec in self:
            report_pdf_data_tuple_requirement = rec.env.ref('mkt_documental_managment.report_documental_requirements').sudo()._render_qweb_pdf(rec.ids)
            report_pdf_data_requirement = report_pdf_data_tuple_requirement[0]
            if report_pdf_data_requirement:
                report_pdf_requirement = io.BytesIO(report_pdf_data_requirement)
                report_pdf_reader_requirement = PyPDF2.PdfFileReader(report_pdf_requirement)
                for page_num in range(report_pdf_reader_requirement.numPages):
                    page_requirement = report_pdf_reader_requirement.getPage(page_num)
                    combined_pdf_writer.addPage(page_requirement)
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', rec._name),
                ('res_id', '=', rec.id),
            ])
            for attachment in attachments:
                if attachment.name.lower().endswith('.pdf') or attachment.mimetype == 'application/pdf':
                    try:
                        pdf_data = io.BytesIO(base64.b64decode(attachment.datas))
                        pdf_reader = PyPDF2.PdfFileReader(pdf_data)
                        
                        for i in range(2):
                            output_pdf = io.BytesIO()
                            pdf_writer = PyPDF2.PdfFileWriter()
                            for page_num in range(pdf_reader.numPages):
                                page = pdf_reader.getPage(page_num)
                                pdf_writer.addPage(page)
                                page.mergePage(self._create_watermark_page(rec.cost_center_id.code, rec.budget_id.name, rec.name))
                            pdf_writer.write(output_pdf)
                            output_pdf.seek(0)
                            pdf_reader = PyPDF2.PdfFileReader(output_pdf)
                            for page_num in range(pdf_reader.numPages):
                                page = pdf_reader.getPage(page_num)
                                combined_pdf_writer.addPage(page)
                    except:
                        raise ValidationError(
                                _( 'The document %s on the requirement %s is not available. Please convert to PDF/A.' ) % ( attachment.name, rec.name )
                            )
                # if attachment.name.lower().endswith(('.png','.jpg','.jpeg')):
                #     image_pdf = self._convert_image_to_pdf(attachment.datas)
                #     combined_pdf_writer.appendPagesFromReader(image_pdf)
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
        can.drawString(10, 5, 'CC:%s %s %s' % ( code, ppto, requirement))
        can.save()
        packet.seek(0)
        return PyPDF2.PdfFileReader(packet).getPage(0)


    # def _convert_image_to_pdf(self, image_data):
    #     image = io.BytesIO(base64.b64decode(image_data))
    #     img_tmp = io.BytesIO()
    #     img_tmp.write(image.getvalue())
    #     img_tmp.seek(0)
        
    #     image_pdf = PyPDF2.PdfFileWriter()
    #     img = PyPDF2.PdfFileReader(img_tmp)
    #     img_page = img.getPage(0)
    #     image_pdf.addPage(img_page)
    #     return image_pdf


    def compute_settlement_amounts(self):
        for rec in self:
            for line in rec.settlement_ids:
                line.compute_amounts()


    def create_refund_requirement(self):
        if self.balance > 0:
            requirement = self.env['documental.requirements'].sudo().create({
                'paid_to': self.full_name.partner_id.id,
                'budget_id': self.budget_id.id,
                'amount_currency_type': self.amount_currency_type,
                'concept': _('Request for reimbursement of expenses incurred for the benefit of the company'),
                'is_refund': True,
                'refund_user_id': self.full_name.id,
                'refund_employee_id': self.full_name.employee_id.id,
                'refund_requirement_id': self.id,
            })
            self.env['settlement'].create({
                'requirement_id': requirement.id,
                'date': fields.Date.today(),
                'dni_ruc': '20512433821',
                'partner': 'MARKETING ALTERNO PERU S.A.C',
                'document_type_id': self.env['settlement.line.type'].search([('short_name','=','FL')]).id,
                'document': self.name,
                'settle_amount': self.balance,
                'reason': _('Refund'),
            })
            self.activity_schedule(
                'mkt_documental_requirement.mail_action_refund_requirement',
                user_id = self.full_name.id,
                summary = _('Refund Requirement created: %s') % ( requirement.name ),
            )


    def compute_balance(self):
        self._compute_balance()


    def button_update_balance(self):
        settlements = self.env['documental.settlements'].search([])
        for settle in settlements:
            settle.requirement_id.balance = settle.balance


    def button_accounting_check(self):
        for rec in self:
            if not rec.account_check:
                rec.account_check = True
            else:
                rec.account_check = False


    def action_view_settlement(self):
        settlement = self.env['documental.settlements'].search([('requirement_id','=',self.id)])
        return {
            'name': _('Settlement'),
            'type': 'ir.actions.act_window',
            'res_model': 'documental.settlements',
            'res_id': settlement.id,
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'target':'current',
        }


    def button_in_bank(self):
        if self.in_bank == True:
            self.in_bank = False
        else:
            self.in_bank = True


    def button_current_rq(self):
        self.ensure_one()
        return {
            'name': _('Aministration Review'),
            'type': 'ir.actions.act_window',
            'res_model': 'documental.requirements',
            'view_mode': 'form',
            'views': [(self.env.ref('mkt_documental_managment.view_requirements_restricted_form').id, 'form')],
            'res_id': self.env['documental.requirements'].search([('id','=',self.id)]).id,
            'target': 'new',
        }


    #* Requirement refuse actions
    def button_refuse_boss(self):
        self = self.sudo()
        self.user_petitioner_signed_id = False
        self.petitioner_signature = False
        self.petitioner_signed_on = False
        self.is_petitioner_signed = False
        self.requirement_state = 'refused'
        self.settlement_refuse_boss()
        self.mobility_unused_validation()


    def button_refuse_budget_executive(self):
        self = self.sudo()
        self.user_boss_signed_id = False
        self.boss_signature = False
        self.boss_signed_on = False
        self.is_boss_signed = False
        self.button_refuse_boss()
        self.settlement_refuse_budget_executive()


    def button_refuse_intern_control(self):
        self = self.sudo()
        self.user_budget_executive_signed_id = False
        self.budget_executive_signature = False
        self.budget_executive_signed_on = False
        self.is_budget_executive_signed = False
        self.intern_control_received = False
        self.button_refuse_budget_executive()
        self.settlement_refuse_intern_control()
        self._compute_settlement_vendor()


    def button_refuse_administration(self):
        self = self.sudo()
        self.user_intern_control_signed_id = False
        self.intern_control_signature = False
        self.intern_control_signed_on = False
        self.is_intern_control_signed = False
        self.intern_control_received = False
        self.button_refuse_intern_control()
        self.settlement_refuse_administration()


    def button_refuse_admin(self):
        self = self.sudo()
        self.user_administration_signed_id = False
        self.administration_signature = False
        self.administration_signed_on = False
        self.is_administration_signed = False
        self.requirement_state = 'administration'
        self.start_time = False        


    def create_requirement_detail(self):
        values = {}
        for rec in self.requirement_detail_ids:
            rec.requirement_detail_line_ids = [(5,0,0)]
            values.update({
                'requirement_detail_id': rec.id,
                'name': rec.reason,
                'service_type_id': rec.service_type_id.id,
                'igv_tax': 'levied',
                'quantity': 1,
                'unit_price': rec.required_amount,
                'tax_igv_id': rec.tax_igv_id.id,
                'igv_included': rec.igv_included,
            })
            self.env['requirement.detail.line'].create(values)


    def create_settlement_line(self):
        values = {}
        for rec in self.settlement_ids:
            rec.line_ids = [(5,0,0)]
            values.update({
                'settlement_id': rec.id,
                'name': rec.reason,
                'service_type_id': rec.service_type_id.id,
                'tax': 'levied',
                'tax_id': rec.tax_id.id,
                'igv_included': rec.igv_included,
                'quantity': 1,
                'unit_price': rec.settle_amount,
            })
            self.env['settlement.line'].create(values)


    def document_format_validation(self):
        for rec in self.settlement_ids:
            if rec.document_type_id.national_format:
                if rec.document:
                    if '-' not in rec.document:
                        raise ValidationError( _('''It is necesary the '-' character in document format.\n
                                                 The correct document name is something like this: FFF1-00000001\n
                                                 It means that on the left hand: Four(4) characters. On the right hand: Eight(8) characters. And no spaces between.''') )
                    else:
                        serie, number = ( rec.document ).split('-')
                        if ( len(serie) != 4 ) or ( len(number) != 8 ):
                            raise ValidationError( _('''It is necesary four(4) characters on the left hand and eight(8) characters on the right hand.\n
                                                     The correct format document name is something like this: FFF1-00000001. And no spaces between.''') )


    def blacklist_validation(self):
        for rec in self:
            if rec.paid_to and rec.paid_to.blacklist:
                raise ValidationError(
                    _(''' - The contact %s is in blacklist. This decision is completly up to the Accounting area.\n
                        - If you think this decision should be reconsidered, please do not hesitate to contact them🙉.
                    ''') % ( rec.paid_to.name )
                )
            for line in rec.settlement_ids:
                if line.dni_ruc:
                    partner = self.env['res.partner'].search([('vat','=',line.dni_ruc)])
                    if partner.blacklist:
                        raise ValidationError(
                            _(''' - The contact %s is in blacklist. This decision is completly up to the Accounting area.\n
                                - If you think this decision should be reconsidered, please do not hesitate to contact them🙉.
                            ''') % ( line.partner )
                        )
            for line in rec.requirement_detail_ids:
                if line.ruc:
                    partner = self.env['res.partner'].search([('vat','=',line.ruc)])
                    if partner.blacklist:
                        raise ValidationError(
                            _(''' - The contact %s is in blacklist. This decision is completly up to the Accounting area.\n
                                - If you think this decision should be reconsidered, please do not hesitate to contact them🙉.
                            ''') % ( line.partner )
                        )


    def maximum_amount_validation(self):
        for rec in self:
            if rec.currency_id.name == 'USD':
                if rec.budget_id.max_amount > 0 and ( rec.amount_uss + rec.budget_id.amount_total ) > rec.budget_id.max_amount:
                    raise ValidationError(_('''Your requirement exceeds the %s of the budget max amount.\n
                                            - If you need to do this Requirement, please contact the budget responsible.
                                            ''') % ( rec.budget_id.max_amount ))
            if rec.currency_id.name == 'PEN':
                if rec.budget_id.max_amount > 0 and ( rec.amount_soles + rec.budget_id.amount_total ) > rec.budget_id.max_amount:
                    raise ValidationError(_('''Your requirement exceeds the %s of the budget max amount.\n
                                            - If you need to do this Requirement, please contact the budget responsible.
                                            ''') % ( rec.budget_id.max_amount ))


    def button_petitioner_signature(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        if self.dni_or_ruc:
            vat = self.dni_or_ruc
            if len(vat) == 11:
                if self.requirement_detail_ids:
                    for rec in self.requirement_detail_ids:
                        if (rec.ruc != self.dni_or_ruc) and rec.document_type.name != 'JUSTIFICACION':
                            raise ValidationError(_('The RUC in the quotation lines does not match with the RUC in the hereby Requirement.'))
        self.write({
            'user_petitioner_signed_id': self.env.user.id,
            'petitioner_signature': signature_generator(user_name),
            'petitioner_signed_on': fields.Datetime.now(),
            'requirement_state': 'executive',
            'is_petitioner_signed': True,
        })
        self.blacklist_validation()
        self.create_requirement_detail()
        self._compute_settlement_vendor()
        self._compute_total_retention()
        self._compute_total_detraction()
        self.mobility_use_validation()
        self.maximum_amount_validation()


    def button_boss_signature(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        self._compute_settlement_vendor()
        self._compute_total_retention()
        self._compute_total_detraction()
        self.write({
            'boss_signature': signature_generator(user_name),
            'is_boss_signed': True,
            'user_boss_signed_id': self.env.user.id,
            'boss_signed_on': fields.Datetime.now(),
            'requirement_state': 'responsible' if self.budget_id.responsible_revision else 'intern_control',
            'intern_control_received': fields.Datetime.now() if not self.budget_id.responsible_revision else False,
        })


    def button_budget_executive_signature(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        self.write({
            'budget_executive_signature': signature_generator(user_name),
            'is_budget_executive_signed': True,
            'requirement_state': 'intern_control',
            'budget_executive_signed_on': fields.Datetime.now(),
            'user_budget_executive_signed_id': self.env.user.id,
            'intern_control_received': fields.Datetime.now(),
        })


    def button_intern_control_signature(self):
        self._compute_settlement_vendor()
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        self.write({
            'intern_control_signature': signature_generator(user_name),
            'is_intern_control_signed': True,
            'requirement_state': 'administration',
            'intern_control_signed_on': fields.Datetime.now(),
            'user_intern_control_signed_id': self.env.user.id,
            })


    def button_administration_signature(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        self.write({
            'administration_signature': signature_generator(user_name),
            'is_administration_signed': True,
            'requirement_state': 'to_settle',
            'administration_signed_on': fields.Datetime.now(),
            'user_administration_signed_id': self.env.user.id,
            'start_time': fields.Datetime.now(),
            })


    # * Settlement signature actions
    def compute_settlement_vendor(self):
        records = self.env['documental.requirements'].search([('total_vendor','=',0),('requirement_state','not in',('draft','refused'))])
        for rec in records:
            rec._compute_settlement_vendor()


    def settlement_petitioner_sign(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name

        self.settlement_attach_files()

        if self.unify:
            self.requirement_state = 'executive'
        else:
            if not self.petitioner_signature:
                raise ValidationError(_('Before signing the settlement, make sure to sign the requirement.'))

        if not self.settlement_ids:
            raise ValidationError(_('Please make sure to write at least one line in the settlement line.'))

        self.document_format_validation()

        self.write({
            'settlement_petitioner_user_id': self.env.user.id,
            'settlement_petitioner_signature': signature_generator(user_name),
            'settlement_petitioner_signed_on': fields.Datetime.now(),
            'settlement_state': 'executive'
        })
        self.blacklist_validation()
        self.create_settlement_line()
        self._compute_settlement_vendor()
        self._compute_total_retention()
        self._compute_total_detraction()
        self.mobility_use_validation()
        self.maximum_amount_validation()


    def compute_total_vendor_retention_detraction(self):
        self._compute_settlement_vendor()
        self._compute_total_retention()
        self._compute_total_detraction()


    def settlement_executive_sign(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        if not self.unify:
            if not self.boss_signature:
                raise ValidationError( _( 'Before to sign the settlement, be sure to sign the requirement.' ) )
        else:
            self.write({
                'requirement_state': 'responsible' if self.budget_id.responsible_revision else 'intern_control',
            })
        self.write({
            'settlement_boss_user_id': self.env.user.id,
            'settlement_boss_signature': signature_generator(user_name),
            'settlement_state': 'responsible' if self.budget_id.responsible_revision else 'intern_control',
            'settlement_intern_control_received': fields.Datetime.now() if self.budget_id.responsible_revision else False,
            'settlement_boss_signed_on': fields.Datetime.now(),
            'timer_state': 'on_time',
        })
        self._compute_settlement_vendor()
        self._compute_total_retention()
        self._compute_total_detraction()

    def settlement_responsible_sign(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        if not self.unify:
            if self.budget_id.responsible_revision:
                if not self.budget_executive_signature:
                    raise ValidationError( _(' Before to sign the settlement, be sure to sign the requirement.') )
        else:
            self.write({
                'requirement_state': 'intern_control',
            })
        self.write({
            'settlement_budget_executive_user_id': self.env.user.id,
            'settlement_budget_executive_signature': signature_generator(user_name),
            'settlement_budget_executive_signed_on': fields.Datetime.now(),
            'settlement_state': 'intern_control',
            'settlement_intern_control_received': fields.Datetime.now(),
        })


    def settlement_intern_control_sign(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        if not self.unify:
            if not self.intern_control_signature:
                raise ValidationError( _( 'Before to sign the settlement, be sure to sign the requirement.' ) )
        else:
            self.write({
                'requirement_state': 'administration'
            })
        self.write({
            'settlement_intern_control_user_id': self.env.user.id,
            'settlement_intern_control_signature': signature_generator(user_name),
            'settlement_intern_control_signed_on': fields.Datetime.now(),
            'settlement_state': 'administration',
        })
        for rec in self.settlement_ids:
            rec.attach_files()


    def settlement_administration_sign(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        if not self.unify:
            if not self.administration_signature:
                raise ValidationError( _( 'Before to sign the settlement, be sure to sign the requirement.' ) )
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
            self.write({
                'settlement_administration_user_id': self.env.user.id,
                'settlement_administration_signature': signature_generator(user_name),
                'settlement_administration_signed_on': fields.Datetime.now(),
                'settlement_state': 'settled',
            })
            self.button_send_to_budget()


    def unlink_attached_files(self):
        attachments = self.env['ir.attachment'].search([
            ('res_model','=',self._name),
            ('res_id','=',self.id),
        ])
        attachments.sudo().unlink()


    # * Settlement refuse actions
    def button_cancel(self):
        budget_lines_obj = self.env['budget.line']
        budget_lines = budget_lines_obj.search([
            ('budget_id','=',self.budget_id.id),
            ('settlement_name','=',self.name)
        ])
        budget_lines.unlink()


    def settlement_refuse_boss(self):
        self = self.sudo()
        self.settlement_petitioner_user_id = False
        self.settlement_petitioner_signature = False
        self.settlement_petitioner_signed_on = False
        self.mobility_unused_validation()
        self.settlement_state = 'refused'
        if self.unify:
            self.requirement_state = 'refused'
        else:
            pass
        self.start_time = False
    

    def settlement_refuse_budget_executive(self):
        self = self.sudo()
        self.settlement_boss_signature = False
        self.settlement_boss_user_id = False
        self.settlement_boss_signed_on = False
        self.settlement_intern_control_received = False
        self.settlement_refuse_boss()


    def settlement_refuse_intern_control(self):
        self = self.sudo()
        self.settlement_budget_executive_signature = False
        self.settlement_budget_executive_signed_on = False
        self.settlement_budget_executive_user_id = False
        self.settlement_refuse_budget_executive()


    def settlement_refuse_administration(self):
        self = self.sudo()
        self.settlement_intern_control_signature = False
        self.settlement_intern_control_signed_on = False
        self.settlement_intern_control_user_id = False
        self.settlement_refuse_intern_control()


    def settlement_refuse_admin(self):
        self = self.sudo()
        self.settlement_administration_signature = False
        self.settlement_administration_signed_on = False
        self.settlement_administration_user_id = False
        self.settlement_state = 'administration'
        self.requirement_state = 'administration' if self.unify else 'to_settle'
        self.button_cancel()


    # * Actions
    def assign_requirement_to_mobility(self):
        requirements = self.env['documental.requirements'].search([])
        for line in requirements:
            for sett in line.settlement_ids:
                if sett.document_type_code == 'PM':
                    mobility = self.env['documental.mobility.expediture'].sudo().search([('name','=',sett.document)])
                    mobility.requirement_id = line.id


    def mobility_use_validation(self):
        for rq_line in self.requirement_detail_ids:
            if rq_line.document_type.short_name == 'PM':
                rq_line.mobility_id.used = True
                rq_line.mobility_id.requirement_id = self.id
        for sett_line in self.settlement_ids:
            if sett_line.document_type_id.short_name == 'PM':
                sett_line.mobility_id.used = True
                sett_line.mobility_id.requirement_id = self.id


    def mobility_unused_validation(self):
        for rq_line in self.requirement_detail_ids:
            if rq_line.document_type.short_name == 'PM':
                rq_line.mobility_id.used = False
                rq_line.mobility_id.requirement_id = False
        for sett_line in self.settlement_ids:
            if sett_line.document_type_id.short_name == 'PM':
                sett_line.mobility_id.used = False
                sett_line.mobility_id.requirement_id = False


    def button_send_to_budget(self):
        values = {}
        for line in self.settlement_ids:
            if line.document_type_id.budgetable == 'yes':
                values.update({
                    'budget_id': self.budget_id.id,
                    # 'documental_settlement_id': line.requirement_id.id,
                    'date': line.date,
                    'document_type': line.document_type_id.name,
                    'document_file': line.document_file,
                    'document_filename': line.document_filename,
                    'document': line.document,
                    'reason': line.reason,
                    'amount': line.settle_amount,
                    'requirement_name': self.name,
                    'settlement_id': line.id,
                    'settlement_name': self.name,
                })
                self.budget_id.budget_line_ids = [(0,0,values)]
        self.settlement_state = 'settled'
        self.requirement_state = 'settled'


    def new_settlement_attach(self):
        records = self.env['documental.requirements'].sudo().search([('settlement_state','not in',('draft','refused')),('create_date','<=',datetime.strptime('26/04/2024', '%d/%m/%Y'))])
        for rec in records:
            attachments = []
            for settlement in rec.settlement_ids:
                if settlement.document_file:
                    attach = {
                        'name': settlement.document_filename,
                        'datas': settlement.document_file,
                        'store_fname': settlement.document_filename,
                        'res_model': rec._name,
                        'res_id': rec.id,
                        'type': 'binary',
                    }
                    attachment = self.env['ir.attachment'].create(attach)
                    attachments.append(attachment.id)


    def settlement_attach_files(self):
        attachments = []
        for settlement in self.settlement_ids:
            if settlement.document_file:
                attach = {
                    'name': settlement.document_filename,
                    'datas': settlement.document_file,
                    'store_fname': settlement.document_filename,
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary',
                }
                attachment = self.env['ir.attachment'].create(attach)
                attachments.append(attachment.id)


    def schedule_check_end_date(self):
        requirements = self.env['documental.requirements'].search([
            ('requirement_state','=','to_settle'),
            ('start_time','!=',False),
            ('settlement_state','not in',('intern_control','administration','settled'))])
        for requirement in requirements:
            mail_obj = self.env['mail.mail']
            if (fields.Datetime.now() - requirement.start_time).days >= 7:
                _logger.info('\n\n\n (fields.Datetime.now() - requirement.start_time).days: %s \n\n\n', (fields.Datetime.now() - requirement.start_time).days)
                requirement.timer_state = 'late'
                subject = 'Recordatorio de Liquidación por %s.' % (requirement.name)
                body = '''Estimado colaborador, liquida tu requerimiento %s!!!\n.
                    Ya han pasado %s días desde que el área de Administración aprobó tu Requerimiento %s por concepto de: %s.
                    Te invitamos a generar, firmar y hacer llegar tu liquidación al área de Control Interno para regularizar tus comprobantes😊.''' % (requirement.name, (fields.Datetime.now() - requirement.start_time).days, requirement.name, requirement.concept)
                email_to = requirement.full_name.login
                mail = mail_obj.create({
                    'subject': subject,
                    'body_html': body,
                    'email_to': email_to,
                })
                mail.send()


    def button_create_transfer(self):
        values = {}
        values.update({
            'requirement_id': self.id,
            'rq_transfer_number': 'O-' + self.operation_number if self.operation_number else ('C-' + self.check_number if self.check_number else ''),
            'rq_payment_date': self.payment_date if self.payment_date else None,
            'rq_budget_id': self.budget_id.id if self.budget_id else None,
            'rq_cost_center_id': self.cost_center_id.id if self.cost_center_id else None,
            'rq_paid_to': self.paid_to.id if self.paid_to else None,
            'rq_concept': self.concept if self.concept else '',
            'rq_currency': self.amount_currency_type if self.amount_currency_type else None,
            'rq_import': 'S/.' + str(round(self.amount_soles,2)) if str(self.amount_soles) else ('$ ' + str(round(self.amount_uss,2)) if str(self.amount_uss) else ''),
            'rq_to_pay_supplier': 'S/.' + str(round(self.to_pay_supplier,2)) if str(self.amount_soles) else ('$ ' + str(round(self.to_pay_supplier,2)) if str(self.amount_uss) else ''),
            'rq_payroll_id': self.requirement_payroll_id.id if self.requirement_payroll_id else None,
            'rq_detraction_amount': self.detraction_amount if self.detraction_amount else None,
            'rq_state': self.state if self.state else None,
        })
        transfer = self.env['report.administration'].search([('requirement_id','=',self.id)])
        if not transfer:
            self.env['report.administration'].create(values)
        else:
            transfer.write(values)


    def button_create_settlement(self):
        if not self.budget_id:
            raise UserError(_('Before creating a Settlement Format, select a budget'))
        else:
            values = {}
            values_detail = {}
            values_line = {}
            values.update({
                'budget_id': self.budget_id.id,
                'cost_center_id': self.cost_center_id.id,
                'campaign_id': self.campaign_id.id,
                'requirement_id': self.id,
                'value': self.amount_soles if self.amount_soles else self.amount_uss,
                'card_payment': self.card_payment,
            })
            settlement = self.env['documental.settlements'].sudo().create(values)
            self.settlement_id = self.env['documental.settlements'].search([('requirement_id','=',self.id)])
            for detail in self.requirement_detail_ids:
                values_detail.update({
                    'documental_settlement_id': settlement.id,
                    'date': detail.date,
                    'ruc': detail.ruc,
                    'partner': detail.partner,
                    'document_type': detail.document_type.id,
                    'document': detail.document,
                    'document_file': detail.document_file,
                    'document_filename': detail.document_filename,
                    'reason': detail.reason,
                    'amount': detail.amount,
                    'to_pay': detail.to_pay,
                    'tax_igv_id': detail.tax_igv_id.id,
                    'detraction_amount': detail.detraction,
                    'retention_amount': detail.retention,
                    'is_taxable': detail.is_taxable,
                    'igv_included': detail.igv_included,
                })
                settlement_detail = self.env['documental.settlements.detail'].create(values_detail)
                for line in detail.requirement_detail_line_ids:
                    values_line.update({
                        'settlement_detail': settlement_detail.id,
                        'name': line.name,
                        'service_type_id': line.service_type_id.id,
                        'igv_tax': line.igv_tax,
                        'tax_igv_id': line.tax_igv_id.id,
                        'quantity': line.quantity,
                        'unit_price': line.unit_price,
                        'base_amount': line.base_amount,
                        'igv': line.igv,
                        'amount': line.amount,
                    })
                    self.env['settlement.detail.line'].create(values_line)


    def modify_requirement_budget(self):
        return {
            'name': 'Modify requirement budget',
            'view_mode': 'form',
            'view_id': self.env.ref('mkt_documental_managment.view_requirement_modify_form').id,
            'view_type': 'form',
            'res_model': 'requirement.modify',
            'type': 'ir.actions.act_window',
            'target': 'new',
        }


    def action_print_pdf(self):
        return self.env.ref('mkt_documental_managment.report_documental_requirements').report_action(self)


    def _get_report_documental_requirement_base_filename(self):
        self.ensure_one()
        return _('Requirement - %s') % (self.name or '')


    def set_line_number(self):
        for rec in self:
            settle_no = 0
            for line in rec.settlement_ids:
                settle_no += 1
                line.settle_no = settle_no
        return


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('documental.requirements') or _('New')
            vals['date'] = datetime.now()
        res = super(DocumentalRequirements, self).create(vals)
        res.set_line_number()
        return res


    def write(self, vals):
        res = super(DocumentalRequirements, self).write(vals)
        self.set_line_number()
        return res


class RequirementDetail(models.Model):
    _name = 'requirement.detail'
    _description = 'Requirement Detail'

    requirement_id = fields.Many2one(comodel_name="documental.requirements", string="Documental Requirement")
    sequence_handle = fields.Integer(string="Sequence handle")
    date = fields.Date(string='Date')
    ruc = fields.Char(string="RUC")
    partner = fields.Char(string="Partner")
    document_type = fields.Many2one(comodel_name="settlement.line.type", string="Document Type", domain="[('visible_in_requirement', '=', True)]", default=lambda self: self._default_document_type())
    document_type_code = fields.Char(related='document_type.short_name', string='Document type code')
    document = fields.Char(string="Document")
    document_file = fields.Binary(string="File")
    document_filename = fields.Char(string="Filename", compute="compute_filename", store=True)
    mobility_id = fields.Many2one(comodel_name='documental.mobility.expediture', domain="[('used','=',False)]", string='Mobility')
    currency_id = fields.Many2one(related='requirement_id.currency_id')
    required_amount = fields.Float(digits=(10,3), string='Required amount')
    required_igv = fields.Float(digits=(10,3), string='Required IGV')
    service_type_id = fields.Many2one(comodel_name="requirement.service.type", string="Service Type")
    reason = fields.Char(string="Reason")
    amount = fields.Monetary(string="Amount", compute="_compute_amount_detraction_to_pay", store=True)
    to_pay = fields.Monetary(string="To Pay", compute="_compute_amount_detraction_to_pay", store=True)
    detraction = fields.Monetary(string="Detraction", compute="_compute_amount_detraction_to_pay", store=True)
    retention = fields.Monetary(string="Retention", compute="_compute_amount_detraction_to_pay", store=True)
    tax_igv_id = fields.Many2one(comodel_name="tax.taxes", string="% IGV", default=get_default_igv, domain="[('tax_type','=','igv')]")
    is_taxable = fields.Boolean(string="Taxable", default=True)
    igv_included = fields.Boolean(string="IGV included?", default=True)
    state = fields.Selection(string="State", related="requirement_id.requirement_state", store=True)
    requirement_detail_line_ids = fields.One2many('requirement.detail.line', 'requirement_detail_id', string="Requirement Detail Line")
    restricted_requirement_detail_line_ids = fields.One2many('requirement.detail.line', 'requirement_detail_id', string="Requirement Detail Line")
    repeated = fields.Boolean(compute='_compute_repeated', default=False, string='Repeated')
    # Campos invisibles controlados
    is_justification = fields.Boolean(string="Is justification?", compute="compute_hide_fields", store=False)


    @api.onchange('document_type')
    def compute_hide_fields(self):
        for record in self:
            if record.document_type and record.document_type.name == 'JUSTIFICACION':
                record.is_justification = True
            else:
                record.is_justification = False


    @api.model
    def _default_document_type(self):
        return self.env['settlement.line.type'].search([('name', '=', 'JUSTIFICACION')], limit=1).id


    @api.onchange('mobility_id','document_type')
    def _onchange_document_type(self):
        zero_igv_id = self.env['tax.taxes'].search([('percentage','=',0)]).id
        if self.document_type_code == 'PM':
            if self.mobility_id:
                self.document = self.mobility_id.name
                self.ruc = self.mobility_id.dni
                self.date = self.mobility_id.date
                self.required_amount = self.mobility_id.amount_total
                self.tax_igv_id = zero_igv_id
        else:
            self.mobility_id = False


    def compute_amount_detraction_to_pay(self):
        self._compute_amount_detraction_to_pay()


    @api.depends('ruc','document_type','document')
    def _compute_repeated(self):
        for rec in self:
            triplet = self.env['requirement.detail'].search(
                [
                    ('id','not in',rec.ids),
                    ('ruc','=',rec.ruc),
                    ('document_type','=',rec.document_type.id),
                    ('document','=',rec.document),
                ]
            )
            if triplet:
                rec.repeated = True
            else:
                rec.repeated = False


    @api.depends('ruc','document')
    def compute_filename(self):
        for rec in self:
            if rec.document_file:
                if rec.ruc and rec.document:
                    rec.document_filename = rec.ruc + '-' + rec.document


    @api.onchange('is_taxable','igv_included', 'requirement_detail_line_ids')
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
                    name = apiperu_ruc(self.ruc)[3]
                    self.partner = name
        else:
            self.partner = False


    @api.depends('requirement_id','service_type_id','required_amount')
    def _compute_amount_detraction_to_pay(self):
        for rec in self:
            sale_change_type = self.env['change.type'].search([('date','=',rec.date)]).mapped('sell')
            change_type = 1
            if len(sale_change_type) != 0 and rec.currency_id.name == 'USD':
                change_type = sale_change_type[0]
            if rec.required_amount * change_type > rec.service_type_id.amount_from:
                if rec.service_type_id.detraction:
                    rec.to_pay = rec.required_amount - round( ( rec.required_amount * rec.service_type_id.percentage ) / 100, 0 )
                    rec.detraction = round( ( rec.required_amount * rec.service_type_id.percentage ) / 100, 0 )
                    rec.retention = 0.00
                if rec.service_type_id.retention:
                    rec.to_pay = rec.required_amount - round( ( rec.required_amount * rec.service_type_id.percentage ) / 100, 2 )
                    rec.detraction = 0.00
                    rec.retention = round( ( rec.required_amount * rec.service_type_id.percentage ) / 100, 2 )
                if not rec.service_type_id.detraction and not rec.service_type_id.retention:
                    rec.to_pay = rec.required_amount
                    rec.detraction = 0.00
                    rec.retention = 0.00
            else:
                rec.to_pay = rec.required_amount
                rec.detraction = 0.00
                rec.retention = 0.00


    # @api.depends('requirement_detail_line_ids')
    # def _compute_amount_detraction_to_pay(self):
    #     for rec in self:
    #         if rec.requirement_detail_line_ids:
    #             rec.amount = sum(rec.requirement_detail_line_ids.mapped('amount'))
    #         else:
    #             rec.amount = 0.00
    #             rec.detraction = 0.00
    #             rec.retention = 0.00
    #             rec.to_pay = 0.00
    #         if rec.requirement_id.amount_currency_type == 'soles':
    #             if rec.is_taxable:
    #                 if rec.requirement_detail_line_ids:
    #                     max_amount_line = rec.env['requirement.detail.line'].search([('requirement_detail_id', '=', rec.id)], order='amount desc', limit=1)
    #                     total_amount = sum(rec.requirement_detail_line_ids.mapped('amount'))
    #                     if total_amount > max_amount_line.service_type_id.amount_from:
    #                         if max_amount_line.service_type_id.detraction == True:
    #                             rec.detraction = round((max_amount_line.service_type_id.percentage * total_amount) / 100, 0)
    #                             rec.to_pay = total_amount - round((max_amount_line.service_type_id.percentage * total_amount) / 100, 0)
    #                             rec.retention = 0.00
    #                         elif max_amount_line.service_type_id.retention == True:
    #                             rec.retention = ( max_amount_line.service_type_id.percentage * total_amount ) / 100
    #                             rec.to_pay = total_amount - ( max_amount_line.service_type_id.percentage * total_amount ) / 100
    #                             rec.detraction = 0.00
    #                         else:
    #                             rec.retention = 0
    #                             rec.detraction = 0
    #                             rec.to_pay = total_amount
    #                     else:
    #                         rec.detraction = 0.0
    #                         rec.retention = 0.00
    #                         rec.to_pay = total_amount
    #             else:
    #                 rec.to_pay = sum(rec.requirement_detail_line_ids.mapped('amount'))
    #                 rec.detraction = 0.00
    #                 rec.retention = 0.00
    #         if rec.requirement_id.amount_currency_type == 'dolares':
    #             if rec.is_taxable:
    #                 if rec.requirement_detail_line_ids:
    #                     max_amount_line = rec.env['requirement.detail.line'].search([('requirement_detail_id', '=', rec.id)], order='amount desc', limit=1)
    #                     total_amount = sum(rec.requirement_detail_line_ids.mapped('amount'))
    #                     sale_change_type = self.env['change.type'].search([('date','=',rec.date)]).mapped('sell')
    #                     if len(sale_change_type) == 0:
    #                         change_type = 0.00
    #                     else:
    #                         change_type = sale_change_type[0]
    #                     if total_amount * change_type > max_amount_line.service_type_id.amount_from:
    #                         if max_amount_line.service_type_id.detraction == True:
    #                             rec.detraction = round((max_amount_line.service_type_id.percentage * total_amount) / 100, 0)
    #                             rec.to_pay = total_amount - round((max_amount_line.service_type_id.percentage * total_amount) / 100, 0)
    #                             rec.retention = 0.00
    #                         elif max_amount_line.service_type_id.retention == True:
    #                             rec.retention = ( max_amount_line.service_type_id.percentage * total_amount ) / 100
    #                             rec.to_pay = total_amount - ( max_amount_line.service_type_id.percentage * total_amount ) / 100
    #                             rec.detraction = 0.00
    #                         else:
    #                             rec.retention = 0
    #                             rec.detraction = 0
    #                             rec.to_pay = total_amount
    #                     else:
    #                         rec.detraction = 0.0
    #                         rec.retention = 0.00
    #                         rec.to_pay = total_amount
    #             else:
    #                 rec.to_pay = sum(rec.requirement_detail_line_ids.mapped('amount'))
    #                 rec.detraction = 0.00
    #                 rec.retention = 0.00


    def action_show_details(self):
        self.ensure_one()
        view = self.env.ref('mkt_documental_managment.view_requirement_detail_form')
        return {
            'name': _('Quotation'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'requirement.detail',
            'views': [(view.id, 'form')],
            'res_id': self.id,
            'target': 'new',
        }


class RequirementDetailJustification(models.Model):
    _name = 'requirement.detail.justification'
    _description = 'Requirement Justification Detail'


    requirement_id = fields.Many2one(comodel_name="documental.requirements", string="Requirement")
    partner = fields.Many2one(comodel_name="res.partner", string="Approval")
    document_file = fields.Binary(string="File")
    document_filename = fields.Char(string="Filename")
    reason = fields.Char(string="Reason")
    amount = fields.Float(string="Amount", digits=(10, 2))


class RequirementDetailLine(models.Model):
    _name = 'requirement.detail.line'
    _description = 'Requirement Detail Line'


    name = fields.Char(string="Description")
    requirement_detail_id = fields.Many2one(comodel_name="requirement.detail", string="Requirement Detail")
    service_type_id = fields.Many2one(comodel_name="requirement.service.type", string="Service Type")
    igv_tax = fields.Selection(selection=[
            ('levied','Levied'),
            ('exonerated','Exonerated'),
            ('surcharge','Surcharge'),
        ], default='levied', string="Tax")
    tax_igv_id = fields.Many2one(comodel_name="tax.taxes", string="% IGV", related="requirement_detail_id.tax_igv_id", store=True)
    igv_included = fields.Boolean(string="IGV included?", related="requirement_detail_id.igv_included", store=True)
    quantity = fields.Integer(string="Quantity", digits=(10, 2))
    unit_price = fields.Float(string="Unit Price", digits=(10, 3))
    base_amount = fields.Float(string="Base Amount", compute="_compute_base_igv_amount", digits=(10, 2), store=True)
    igv = fields.Float(string="IGV", compute="_compute_base_igv_amount", digits=(10, 2), store=True)
    amount = fields.Float(string="Amount", compute="_compute_base_igv_amount", digits=(10, 2), store=True)

    def compute_base_igv_amount(self):
        self._compute_base_igv_amount()


    @api.depends('quantity', 'unit_price', 'igv_included', 'igv_tax', 'tax_igv_id')
    def _compute_base_igv_amount(self):
        for rec in self:
            if rec.requirement_detail_id.igv_included == True:
                if rec.igv_tax == 'levied':
                    rec.base_amount = ( rec.quantity * rec.unit_price ) / ( 1 + ( rec.tax_igv_id.percentage / 100 ) )
                    rec.igv = ( ( rec.quantity * rec.unit_price ) / ( 1 + ( rec.tax_igv_id.percentage / 100 ) ) ) * (rec.tax_igv_id.percentage / 100)
                    rec.amount = rec.quantity * rec.unit_price
                if rec.igv_tax in ('exonerated','surcharge'):
                    rec.base_amount = rec.quantity * rec.unit_price
                    rec.igv = 0.00
                    rec.amount = rec.quantity * rec.unit_price
            else:
                if rec.igv_tax == 'levied':
                    rec.base_amount = rec.quantity * rec.unit_price
                    rec.igv = ( rec.quantity * rec.unit_price ) * ( rec.tax_igv_id.percentage / 100 )
                    rec.amount = ( rec.quantity * rec.unit_price ) + ( ( rec.quantity * rec.unit_price ) * ( rec.tax_igv_id.percentage / 100 ) )
                if rec.igv_tax in ('exonerated','surcharge'):
                    rec.base_amount = rec.quantity * rec.unit_price
                    rec.igv = 0.00
                    rec.amount = rec.quantity * rec.unit_price


class RequirementPayroll(models.Model):
    _name = 'requirement.payroll'
    _description = 'Requirement Payroll Type'
    _rec_name = "code"

    name = fields.Char(string="Name")
    code = fields.Char(string="Code")
