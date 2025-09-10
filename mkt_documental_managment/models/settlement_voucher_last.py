from odoo import models, fields, tools

class SettlementVoucherLast(models.Model):
    _name = 'settlement.voucher.last'
    _description = 'Último correlativo por subdiario'
    _auto = False
    _table = 'settlement_voucher_last'
    _order = 'accountable_year_id desc, accountable_month_id desc, subdiary asc'

    id = fields.Integer(string="ID", readonly=True)
    accountable_year_id = fields.Many2one('years', string="Año contable", readonly=True)
    accountable_month_id = fields.Many2one('months', string="Mes contable", readonly=True)
    subdiary = fields.Char(string="Subdiario", size=4, readonly=True)
    voucher_number = fields.Char(string='Último correlativo', readonly=True)

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS (
                {self._select()}
                {self._from()}
                {self._where()}
            )
        """)

    def _select(self):
        return """
            SELECT
                ROW_NUMBER() OVER (
                    ORDER BY sub.accountable_year DESC, sub.accountable_month_id DESC, sub.subdiary
                ) AS id,
                y.id                         AS accountable_year_id,
                sub.accountable_month_id     AS accountable_month_id,
                sub.subdiary                 AS subdiary,
                sub.voucher_number           AS voucher_number
        """

    def _from(self):
        return """
            FROM (
                SELECT
                    s.accountable_month_id,
                    s.subdiary,
                    s.voucher_number,
                    EXTRACT(YEAR FROM COALESCE(s.date, s.create_date))::int AS accountable_year,
                    s.id AS sid,
                    ROW_NUMBER() OVER (
                        PARTITION BY
                            EXTRACT(YEAR FROM COALESCE(s.date, s.create_date))::int,
                            s.accountable_month_id,
                            s.subdiary
                        ORDER BY
                            COALESCE(NULLIF(regexp_replace(s.voucher_number, '\\D', '', 'g'), '')::bigint, 0) DESC,
                            s.id DESC
                    ) AS rn
                FROM settlement s
                WHERE s.voucher_number IS NOT NULL
                  AND s.accountable_month_id IS NOT NULL
                  AND s.subdiary IS NOT NULL
                  AND COALESCE(s.date, s.create_date) IS NOT NULL
            ) AS sub
            LEFT JOIN years y
                ON y.number ~ '^[0-9]{4}$'
               AND y.number::int = sub.accountable_year
        """

    def _where(self):
        return """
            WHERE sub.rn = 1
        """

    def _join(self):
        return ""
