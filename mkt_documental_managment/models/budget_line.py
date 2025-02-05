from odoo import _, fields, models
from datetime import datetime

class BudgetLines(models.Model):
    _name = 'budget.line'
    _description = 'Budget Control Line'

    budget_id = fields.Many2one(comodel_name="budget", string="Budget")
    settlement_id = fields.Many2one(comodel_name='settlement', string='settlement')
    documental_settlement_id = fields.Many2one(comodel_name="documental.settlements")
    requirement_id = fields.Many2one(related="documental_settlement_id.requirement_id", string="Requirement")
    settlement_name = fields.Char(string="Settlement")
    requirement_name = fields.Char(string='Requirement')
    settlement_detail_id = fields.Many2one(comodel_name="documental.settlements.detail", string="Settlement Detail")
    date = fields.Date(string="Date", default=datetime.now())
    document_filename = fields.Char(string="File Name", store=True)
    document_file = fields.Binary(string="File")
    document_type = fields.Char(string="Document Type")
    document = fields.Char(string="Document")
    reason = fields.Char(string="Reason")
    amount = fields.Float(string="Amount")
    cotized = fields.Boolean(string="Cotized", default=False)
    remove = fields.Boolean(default=False, string='Remove')
    state = fields.Selection(related='budget_id.state', string='State')