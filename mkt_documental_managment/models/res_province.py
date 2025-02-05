from odoo import _, api, fields, models


class ResProvince(models.Model):
    _name = 'res.province'
    _description = 'Res Province'
    _order = 'id desc'

    name = fields.Char(copy=False, string="Province", required=True)
