from odoo import fields, models

class Years(models.Model):
    _name = 'years'
    _description = 'Years'

    number = fields.Char(required=True, string='Year Number')
    open_year = fields.Boolean(string='Activate', default=True)

    def name_get(self):
        return [(rec.id, rec.number) for rec in self]