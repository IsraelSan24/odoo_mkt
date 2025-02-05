from odoo import api, models, fields


class PhotocheckSupervisor(models.Model):
    _name = "photocheck.supervisor"
    _description = "Photocheck Supervisor"

    name = fields.Char(string='Name')
    user_id = fields.Many2one(comodel_name='res.users', string='Supervisor')
    brand_group_ids = fields.Many2many(comodel_name='photocheck.brand.group', string='Brand Groups')