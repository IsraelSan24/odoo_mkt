from odoo import _, fields, models

class ResPartnerBrand(models.Model):
    _name = 'res.partner.brand'
    _description = 'Partner Brand'
    
    name = fields.Char(string='Brand')
    logo = fields.Image(string='Logo')
    user_id = fields.Many2one(comodel_name='res.users', default=lambda self: self.env.user, string='Responsible')
