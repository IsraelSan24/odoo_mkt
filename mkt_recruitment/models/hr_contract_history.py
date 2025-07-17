from odoo import models, fields


class ContractHistory(models.Model):
    _inherit = 'hr.contract.history'

    state = fields.Selection(selection_add=[('signed', 'Signed')])