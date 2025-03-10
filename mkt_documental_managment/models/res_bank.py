from odoo import models, fields

class ResBank(models.Model):
    _inherit = 'res.bank'

    account_id = fields.Many2one(
        'account.account', 
        string="Cuenta Contable",
        domain="[('account_type', 'in', ['asset_cash', 'bank'])]",  # Solo cuentas de banco o efectivo
        help="Cuenta contable asociada a este banco."
    )