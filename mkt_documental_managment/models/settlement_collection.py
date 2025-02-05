from odoo import _, fields, models, tools


class SettlementCollection(models.Model):
    _name = 'settlement.collection'
    _description = 'Settlement collection'
    _auto = False

    name = fields.Char(string="Settlement")
    date = fields.Date(string="Date")
    ruc = fields.Char(string="RUC")
    partner = fields.Char(string="Partner")
    document_type = fields.Char(string="Document type")
    document = fields.Char(string="Document")
    reason = fields.Char(string="Reason")
    to_pay = fields.Float(string="To pay")
    detraction_total = fields.Float(string="Detraction total")
    amount_total = fields.Float(string="Amount total")


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self._cr.execute(""" CREATE or REPLACE VIEW %s AS (
            %s
            FROM %s AS dsd
            %s                
            )""" %(self._table, self._select(), self._from(), self._join()))


    def _select(self):
        select = """
            SELECT
                dsd.id AS id,
                ds.name AS name,
                dsd.date AS date,
                dsd.ruc AS ruc,
                dsd.partner AS partner,
                slt.name AS document_type,
                dsd.document AS document,
                dsd.reason AS reason,
                dsd.to_pay AS to_pay,
                dsd.detraction_amount AS detraction_total,
                dsd.amount AS amount_total         
        """
        return select


    def _from(self):
        return 'documental_settlements_detail'


    def _join(self):
        join = """
            LEFT JOIN documental_settlements AS ds ON ds.id=dsd.documental_settlement_id
            LEFT JOIN settlement_line_type AS slt ON slt.id = dsd.document_type
            ORDER BY ds.name desc
        """
        return join