from odoo import _, api, fields, models

class BudgetCampaign(models.Model):
    _name = 'budget.campaign'
    _description = 'Budget Campaign'

    name = fields.Char(string="Campaign Description", required=True)
    user_id = fields.Many2one(comodel_name="res.users", string="User", default=lambda self: self.env.user)
