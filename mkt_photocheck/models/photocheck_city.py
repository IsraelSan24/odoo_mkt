from odoo import fields, models

class PhotocheckCity(models.Model):
    _name = 'photocheck.city'
    _description = 'Photocheck City'

    name = fields.Char(string="City", required=True)