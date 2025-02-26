from odoo import _, fields, models

class CostCenter(models.Model):
    _name = 'cost.center'
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = 'Cost Center(CC)'
    _rec_name = 'code'


    name = fields.Char(string="Name", required=True, tracking=True)
    code = fields.Char(string="Cost center number", required=True, tracking=True)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Social Reason", required=True)
    province_id = fields.Many2one(comodel_name="res.province", string="Province", required=True)
    partner_brand_id = fields.Many2one(comodel_name="res.partner.brand", string="Brand", required=True)
    executive_id = fields.Many2one(comodel_name="res.users", string="Executive")
    responsible_id = fields.Many2one(comodel_name="res.users", string="Responsible")
    external_control_revision = fields.Boolean(default=False, string="Requiered external control revision?")

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name must be unique.')
    ]
