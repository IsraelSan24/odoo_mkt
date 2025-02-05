from odoo import models, fields

class PhotocheckJob(models.Model):
    _name = 'photocheck.job'
    _description = 'Photocheck Job'
    
    name = fields.Char(string="Job", required=True)