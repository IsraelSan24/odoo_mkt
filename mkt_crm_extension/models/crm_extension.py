from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    brand = fields.Char(string="Brand")