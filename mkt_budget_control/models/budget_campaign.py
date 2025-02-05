from odoo import _, api, fields, models

class BudgetCampaign(models.Model):
    _name = 'budget.campaign'
    _description = 'Budget Campaign'

    # name = fields.Char(copy=False, default=lambda self: _('New'), required=True)
    # campaign = fields.Char(string="Campaign Description", required=True)
    name = fields.Char(string="Campaign Description", required=True)
    user_id = fields.Many2one(comodel_name="res.users", string="User", default=lambda self: self.env.user)


    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('campaign') or _('New')
    #     return super(BudgetCampaign, self).create(vals)