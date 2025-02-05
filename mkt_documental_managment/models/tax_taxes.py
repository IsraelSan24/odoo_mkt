from odoo import _, api, fields, models

class TaxTaxes(models.Model):
    _name = 'tax.taxes'
    _description = 'Taxes'


    name = fields.Char(name='Name', copy=False)
    percentage = fields.Float(name='Percetange Tax')
    tax_type = fields.Selection(selection=[
            ('igv','IGV'),
            ('income_tax','Income tax'),
        ], string='Income tax')
