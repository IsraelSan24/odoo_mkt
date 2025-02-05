from odoo import _, api, fields, models

rq_state = [
    ('draft', 'Draft'),
    ('waiting_boss_validation', 'Waiting Boss Validation'),
    ('waiting_budget_executive_validation', 'Waiting Budget Executive Validation'),
    ('waiting_intern_control_validation', 'Waiting Intern Control Validation'),
    ('waiting_administration_validation', 'Waiting Administration Validation'),
    ('to_settle', 'To Settle'),
    ('settled', 'Settled'),
    ('refused', 'Refused'),
]

st_state = [
    ('draft', 'Draft'),
    ('waiting_boss_validation','Waiting Boss Validation'),
    ('waiting_budget_executive_validation','Waiting Budget Executive Validation'),
    ('waiting_intern_control_validation','Waiting Intern Control Validation'),
    ('waiting_administration_validation','Waiting Administration Validation'),
    ('settled','Settled'),
    ('refused','Refused')
]

class Voucher(models.Model):
    _name = 'voucher'
    _description = 'Voucher'
    _order = 'id desc'

    name = fields.Char(copy=False, default=lambda self:_('New'), required=True, string='Name')
    requirement_id = fields.Many2one(comodel_name="documental.requirements", string="Requirement")
    paid_partner_id = fields.Many2one(comodel_name="res.partner", related="requirement_id.paid_to", string="Paid to")
    vat_paid_partner = fields.Char(string="DNI or RUC", related="requirement_id.dni_or_ruc")
    card = fields.Boolean(string="Payment Card", related="requirement_id.card_payment")
    bank_id = fields.Many2one(comodel_name="res.bank", string="Bank", related="requirement_id.bank")
    account_bank = fields.Char(string="Account bank", related="requirement_id.customer_account_number")
    budget_id = fields.Many2one(comodel_name="budget", related="requirement_id.budget_id", string="Budget")
    cost_center_id = fields.Many2one(comodel_name="cost.center", related="requirement_id.cost_center_id", string="Cost center")
    partner_id = fields.Many2one(comodel_name="res.partner", related="requirement_id.partner_id", string="Customer")
    year_month_id = fields.Many2one(comodel_name="year.month", related="requirement_id.year_month_id", string="Month/Year")
    campaign_id = fields.Many2one(comodel_name="budget.campaign", related="requirement_id.campaign_id", string="Campaign")
    currency = fields.Selection(string="Currency", related="requirement_id.amount_currency_type")
    currency_id = fields.Many2one(comodel_name='res.currency', related='requirement_id.currency_id')
    # amount_soles = fields.Float(related="requirement_id.amount_soles", string="Amount(S/.)")
    amount_soles = fields.Monetary(related="requirement_id.amount_soles", currency_field='currency_id', string="Amount(S/.)")
    # amount_uss = fields.Float(related="requirement_id.amount_uss", string="Amount(USS)")
    amount_uss = fields.Monetary(related="requirement_id.amount_uss", currency_field='currency_id', string="Amount(USS)")
    amount_char = fields.Char(related="requirement_id.amount_char", string="For the sum of")
    concept = fields.Char(related="requirement_id.concept", string="Concept")
    detail = fields.Char(related="requirement_id.detail", string="Detail")
    user_id = fields.Many2one(comodel_name="res.users", related="requirement_id.full_name", string="Petitioner")
    check_or_operation = fields.Selection(related='requirement_id.check_or_operation', string='Check/Operation')
    check_number = fields.Char(related='requirement_id.check_number', string='Check number')
    operation_number = fields.Char(related='requirement_id.operation_number', string='Operation number')
    payment_date = fields.Date(related='requirement_id.payment_date', string='Payment date')
    requirement_state = fields.Selection(selection=rq_state, related='requirement_id.state', string='Requirement state')
    approved_by = fields.Char(string="Approved by")


    settled_amount = fields.Float(string="Settled amount", digits=(10,2))
    settled_igv_amount = fields.Float(string="Settled igv amount", digits=(10,2))
    settled_detraction_amount = fields.Float(string="Settled detraction amount", digits=(10,2))
    settled_retention_amount = fields.Float(string="Settled retention amount", digits=(10,2))
    settled_total_amount_char = fields.Char(string='Settled amount char', related='settlement_id.total_amount_char')
    settlement_id = fields.Many2one(comodel_name="documental.settlements", related="requirement_id.settlement_id", string="Settlement")
    settlement_state = fields.Selection(selection=st_state, related='settlement_id.state', string='Settlement state')
    justification_ids = fields.One2many(related="requirement_id.restricted_requirement_detail_justification_ids", string="Justification")
    document_ids = fields.One2many(related="requirement_id.restricted_requirement_detail_ids", string="Document")
    settlement_line_ids = fields.One2many(related="settlement_id.restrict_settlement_detail_ids", string="Settlement Line")

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('voucher') or _('New')
        return super(Voucher, self).create(vals)