from odoo import _, fields, models

class PhotocheckBrandGroup(models.Model):
    _name = 'photocheck.brand.group'
    _description = 'Photocheck Brand Group'
    
    name = fields.Char(string='Name')
    brand_ids = fields.Many2many(comodel_name='res.partner.brand', string="Brand")
    responsible_id = fields.Many2one(comodel_name='res.users', string='Responsible')