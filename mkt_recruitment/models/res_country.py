from odoo import fields, models

class ResCountry(models.Model):
    _inherit = 'res.country'
    
    demonym = fields.Char(string='Demonym')