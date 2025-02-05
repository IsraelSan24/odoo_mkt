from odoo import _, fields, models

class CostCenter(models.Model):
    _name = 'cost.center'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Cost Center'
    _rec_name = 'code'

    name = fields.Char(required=True, string='Name', tracking=True)
    code = fields.Char(required=True, string='Cost center number', tracking=True)
    partner_id = fields.Many2one(comodel_name='res.partner', required=True, string='Social Reason')
    province_id = fields.Many2one(comodel_name='res.province', required=True, string='Province')
    partner_brand_id = fields.Many2one(comodel_name='res.partner.brand', required=True, string='Brand')
    executive_id = fields.Many2one(comodel_name='res.users', string='Executive')
    responsible_id = fields.Many2one(comodel_name='res.users', string='Responsible')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique.')
    ]
