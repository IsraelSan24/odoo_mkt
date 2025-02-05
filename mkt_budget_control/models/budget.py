from odoo import _, api, fields, models
from datetime import datetime

state = [
    ('draft','Draft'),
    ('active','Active'),
    ('closed','Closed'),
    ('locked','Locked'),
    ('canceled','Canceled'),
]


class BudgetLines(models.Model):
    _name = 'budget.line'
    _description = 'Budget Control Line'

    budget_id = fields.Many2one(comodel_name="budget", string="Budget")
    documental_settlement_id = fields.Many2one(comodel_name="documental.settlements")
    settlement_name = fields.Char(string="Settlement")
    settlement_detail_id = fields.Many2one(comodel_name="documental.settlements.detail", string="Settlement Detail")
    date = fields.Date(string="Date", default=datetime.now())
    document_filename = fields.Char(string="File Name", store=True)
    document_file = fields.Binary(string="File")
    document_type = fields.Char(string="Document Type")
    document = fields.Char(string="Document")
    reason = fields.Char(string="Reason")
    amount = fields.Float(string="Amount")
    cotized = fields.Boolean(string="Cotized", default=False)
