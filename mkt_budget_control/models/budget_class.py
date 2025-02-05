from odoo import _, api, fields, models

class BudgetClass(models.Model):
    _name = 'budget.class'
    _description = 'Budget Class'

    name = fields.Char(string="Class", required=True)