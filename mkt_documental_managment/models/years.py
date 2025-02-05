from odoo import fields, models

class Years(models.Model):
    _name = 'years'
    _description = 'Years'
    
    name = fields.Char(required=True, string='Name')