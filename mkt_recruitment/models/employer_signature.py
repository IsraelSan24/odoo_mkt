from odoo import _, fields, models

class EmployerSignature(models.Model):
    _name = 'employer.signature'
    _description = 'Employer signature'

    name = fields.Char(string='Name')
    signature_default = fields.Boolean(default=False, string='Signature by default')
    signature = fields.Image(string='Signature')
