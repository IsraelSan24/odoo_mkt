from odoo import _, api, fields, models

class SettlementLineJournal(models.Model):
    _name = 'settlement.line.journal'
    _description = 'Settlement line journal'

    settlement_detail_id = fields.Many2one(comodel_name="documental.settlements.detail", string="Settlement detail")
    name = fields.Char(string="Description")
    account_id = fields.Many2one(comodel_name="account.account", string="Account")
    account_code = fields.Char(related="account_id.code", string="Account code")
    cost_center_id = fields.Many2one(comodel_name="cost.center", string="Cost center", size=6)
    debit = fields.Float(string="Debit", default=0.0, digits=(10,2))
    credit = fields.Float(string="Credit", default=0.0, digits=(10,2))
    annex_code = fields.Char(string="Annex Code", size=18)
    document_number = fields.Char(string="Document number")
    auxiliar_annex_code = fields.Char(string="Auxiliar annex code")
    reference_document_type = fields.Char(string="Reference document type")
    reference_document_number = fields.Char(string="Reference document number")
    reference_document_date = fields.Date(string="Reference document date")
    rate_type = fields.Char(string="Rate type")
    detraction_retention_type = fields.Float(string="Detraction/Retention type", digits=(10,2))
    soles_detraction_perception_amount = fields.Float(string="Base Amount Detraction/Perception Soles")