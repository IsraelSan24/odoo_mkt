from odoo import _, fields, models

class ResPartnerBrand(models.Model):
    _name = 'res.partner.brand'
    _description = 'A simple brand'

    name = fields.Char(string="Brand", required=True)
