from odoo import _, api, fields, models, tools

state = [
    ('draft', 'Draft'),
    ('waiting_boss_validation', 'Waiting Boss Validation'),
    ('waiting_intern_control_validation', 'Waiting Intern Control Validation'),
    ('waiting_administration_validation', 'Waiting Administration Validation'),
    ('to_settle', 'To Settle'),
    ('settled', 'Settled'),
    ('refused', 'Refused'),
]

currency_type = [
    ('soles', 'Soles'),
    ('dolares', 'Dólares'),
]

class ReportAdministration(models.Model):
    _name = 'report.administration'
    _description = 'Administration Report'
    _rec_name = 'rq_transfer_number'

    requirement_id = fields.Many2one(comodel_name="documental.requirements", string="Requirement")
    rq_transfer_number = fields.Char(string="Operation Number")
    rq_payment_date = fields.Date(string="Payment Date")
    rq_budget_id = fields.Many2one(comodel_name="budget", string="Budget")
    rq_cost_center_id = fields.Many2one(comodel_name="cost.center", string="Cost Center")
    rq_paid_to = fields.Many2one(comodel_name="res.partner", string="Provider")
    rq_concept = fields.Char(string="Concept")
    rq_currency = fields.Selection(string="Currency", selection=currency_type)
    rq_import = fields.Char(string="Import")
    rq_detraction_amount = fields.Float(string="Detraction")
    rq_to_pay_supplier = fields.Char(string="To pay supplier")
    rq_payroll_id = fields.Many2one(comodel_name="requirement.payroll", string="Payroll")
    rq_state = fields.Selection(string="State", selection=state)

    settlement_id = fields.Many2one(comodel_name="documental.settlements", string="Settlement")
    # st_total_amount = fields.Float(string="Total Amount")
    
    rq_st_return_employee = fields.Char(string="Return to Employee", compute='compute_returns')
    rq_st_return_mkt = fields.Char(string="Return to MKT", compute='compute_returns')

    transfer_line_ids = fields.One2many("report.administration.line", "report_administration_id", string="Report Line")

    @api.depends('requirement_id')
    def compute_returns(self):
        for rec in self:
            if rec.requirement_id.amount_soles:
                settlement_amount_soles = 0
                for line in rec.transfer_line_ids:
                    settlement_amount_soles += line.amount
                if rec.requirement_id.amount_soles > settlement_amount_soles:
                    rec.rq_st_return_employee = 'S/.0.00'
                    rec.rq_st_return_mkt = 'S/.' + str(round(rec.requirement_id.amount_soles - settlement_amount_soles,2))
                else:
                    rec.rq_st_return_employee = 'S/.' + str(round(settlement_amount_soles - rec.requirement_id.amount_soles,2))
                    rec.rq_st_return_mkt = 'S/.0.00'
            if rec.requirement_id.amount_uss:
                settlement_amount_uss = 0
                for line in rec.transfer_line_ids:
                    settlement_amount_uss += line.amount
                if rec.requirement_id.amount_uss > settlement_amount_uss:
                    rec.rq_st_return_employee = '$0.00'
                    rec.rq_st_return_mkt = '$' + str(round(rec.requirement_id.amount_uss - settlement_amount_uss,2))
                else:
                    rec.rq_st_return_employee = '$' + str(round(settlement_amount_uss - rec.requirement_id.amount_uss,2))
                    rec.rq_st_return_mkt = '$0.00'

class SettlementTransfer(models.Model):
    _name = 'report.administration.line'
    _description = 'Administration Report Line'

    report_administration_id = fields.Many2one(comodel_name="report.administration", string="Transfers")
    documental_settlement_id = fields.Many2one(comodel_name="documental.settlements")
    settlement_name = fields.Char(string="Settlement")
    date = fields.Date(string="Date")
    document_filename = fields.Char(string="File Name", store=True)
    document_file = fields.Binary(string="File")
    document_type = fields.Char(string="Document Type")
    document = fields.Char(string="Document")
    reason = fields.Char(string="Reason")
    amount = fields.Float(string="Amount")