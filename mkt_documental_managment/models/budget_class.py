from odoo import _, fields, models

class BudgetClass(models.Model):
    _name = 'budget.class'
    _description = 'Budget Class'

    name = fields.Char(string="Class", required=True)