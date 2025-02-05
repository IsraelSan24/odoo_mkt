from odoo import _, fields, models

class ResProvince(models.Model):
    _name = 'res.province'
    _description = 'Res Province'
    _order = 'id desc'

    name = fields.Char(copy=False, string='Province', required=True)
    user_id = fields.Many2one(comodel_name='res.users', readonly=True, default=lambda self:self.env.user, string='Responsible')