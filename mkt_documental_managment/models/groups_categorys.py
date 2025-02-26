from odoo import _, fields, models

class GroupsCategorys(models.Model):
    _name = 'groups.categorys'

    name = fields.Char(string='Name')