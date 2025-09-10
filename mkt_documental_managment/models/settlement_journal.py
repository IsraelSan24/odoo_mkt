from odoo import _, api, fields, models

class SettlementJournal(models.Model):
    _name = 'settlement.journal'
    _description = 'Settlement journal'

    settlement_id = fields.Many2one('settlement', string='Settlement')
    name = fields.Char(string='Description')
    account_id = fields.Many2one('account.account', string='Account')
    account_code = fields.Char(related='account_id.code', string='Account code', store=False)
    cost_center_id = fields.Many2one('cost.center', string='Cost center')
    debit = fields.Float(default=0.0, digits=(10, 2), string='Debit')
    credit = fields.Float(default=0.0, digits=(10, 2), string='Credit')
    annex_code = fields.Char(string='Annex code', size=18)
    document_number = fields.Char(string='Document number')
    auxiliar_annex_code = fields.Char(string='Auxiliar annex code')
    reference_document_type = fields.Char(string='Reference document type')
    reference_document_number = fields.Char(string='Reference document number')
    reference_document_date = fields.Date(string='Reference document date')
    rate_type = fields.Char(string='Rate type')
    detraction_retention_type = fields.Float(digits=(10, 2), string='Det/Ret type')
    soles_detraction_retention_amount = fields.Float(string='Base amount det/ret soles')


    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        settlement_id = self.env.context.get('default_settlement_id')
        if settlement_id:
            first = self.search([('settlement_id', '=', settlement_id)], order='id asc', limit=1)
            if first:
                res.setdefault('cost_center_id', first.cost_center_id.id or False)
                res.setdefault('annex_code', first.annex_code or False)
                res.setdefault('document_number', first.document_number or False)
        return res


    @api.model
    def create(self, vals):
        if vals.get('settlement_id'):
            missing = any(not vals.get(k) for k in ('cost_center_id', 'annex_code', 'document_number'))
            if missing:
                first = self.search([('settlement_id', '=', vals['settlement_id'])], order='id asc', limit=1)
                if first:
                    vals.setdefault('cost_center_id', first.cost_center_id.id or False)
                    vals.setdefault('annex_code', first.annex_code or False)
                    vals.setdefault('document_number', first.document_number or False)
        return super().create(vals)


    @api.onchange('settlement_id')
    def _onchange_copy_from_first(self):
        for rec in self:
            if not rec.settlement_id:
                continue
            others = rec.settlement_id.journal_ids - rec
            if not others:
                continue
            first = others.sorted('id')[:1]
            if first:
                if not rec.cost_center_id:
                    rec.cost_center_id = first.cost_center_id
                if not rec.annex_code:
                    rec.annex_code = first.annex_code
                if not rec.document_number:
                    rec.document_number = first.document_number
