from odoo import _, fields, models, api

class PhotocheckBrandGroup(models.Model):
    _name = 'photocheck.brand.group'
    _description = 'Photocheck Brand Group'
    
    name = fields.Char(string='Name')
    brand_ids = fields.Many2many(comodel_name='res.partner.brand', string="Brand")
    
    responsible_lines = fields.One2many(
        "photocheck.brand.group.responsible",
        "brand_group_id",
        string="Responsibles"
    )