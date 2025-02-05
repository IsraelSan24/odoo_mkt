from odoo import fields, models

class Months(models.Model):
    _name = 'months'
    _description = 'Months'
    
    name = fields.Char(required=True, string='Name')
    number = fields.Char(required=True, string='Number')
    open_month = fields.Boolean(string='Activate', default=True)
