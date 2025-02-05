from odoo import fields, models

class ContractType(models.Model):
    _inherit = 'hr.contract.type'
    
    contract_short_name = fields.Char(string='Short name of contract')
