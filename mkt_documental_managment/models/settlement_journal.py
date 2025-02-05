from odoo import _, fields, models

class SettlementJournal(models.Model):
    _name = 'settlement.journal'
    _description = 'Settlement journal'

    settlement_id = fields.Many2one(comodel_name='settlement', string='Settlement')
    name = fields.Char(string='Description')
    account_id = fields.Many2one(comodel_name='account.account', string='Account')
    account_code = fields.Char(related='account_id.code', string='Account code')
    cost_center_id = fields.Many2one(comodel_name='cost.center', string='Cost center', size=6)
    debit = fields.Float(default=0.0, digits=(10,2), string='Debit')
    credit = fields.Float(default=0.0, digits=(10,2), string='Credit')
    annex_code = fields.Char(string='Annex code', size=18)
    document_number = fields.Char(string='Document number')
    auxiliar_annex_code = fields.Char(string='Auxiliar annex code')
    reference_document_type = fields.Char(string='Reference document type')
    reference_document_number = fields.Char(string='Reference document number')
    reference_document_date = fields.Date(string='Reference document date')
    rate_type = fields.Char(string='Rate type')
    detraction_retention_type = fields.Float(digits=(10,2), string='Det/Ret type')
    soles_detraction_retention_amount = fields.Float(string='Base amount det/ret soles')