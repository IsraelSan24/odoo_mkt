from odoo import _, api, fields, models, tools


state = [
    ('draft', 'Draft'),
    ('waiting_boss_validation', 'Waiting Boss Validation'),
    ('waiting_intern_control_validation', 'Waiting Intern Control Validation'),
    ('waiting_administration_validation', 'Waiting Administration Validation'),
    ('settled', 'Settled'),
    ('refused','Refused')
]

class ExpensesControlReport(models.Model):
    _name = 'expenses.control.report'
    _auto = False
    _order = 'id desc'

    dr_date = fields.Datetime(string="Requirement Date")
    dr_budget = fields.Char(string="Budget")
    dr_cc_code = fields.Char(string="Cost Center")
    dr_card_payment = fields.Char(string="Card Payment")
    dr_paid_to = fields.Char(string="Paid to")
    dr_name = fields.Many2one(comodel_name="documental.requirements", string="Requirement")
    dr_currency = fields.Char(string="Currency")
    # dr_rounded_amount = fields.Char(string="Requirement Import")
    dr_rounded_amount = fields.Float(string="Requirement Import")
    dr_settlement = fields.Char(string="Settlement")
    ds_date = fields.Datetime(string="Settlement Date")
    dsd_date = fields.Date(string="Settlement Detail Date")
    dsd_document_type = fields.Char(string="Document Type")
    dsd_document = fields.Char(string="Document")
    dsd_reason = fields.Char(string="Reason")
    dsd_amount = fields.Float(string="Amount")
    ds_total_import = fields.Float(string="Total Import")
    dsd_igv_total = fields.Float(string="Total IGV")
    dsd_tax_perc = fields.Char(string="IGV(%)")
    dsd_total_amount_base = fields.Float(string="Without IGV")
    # refund_employee = fields.Char(string="Refund to employee")
    refund_employee = fields.Float(string="Refund to employee")
    # refund_mkt = fields.Char(string="Refund to MKT")
    refund_mkt = fields.Float(string="Refund to MKT")
    # ds_state = fields.Char(string="Observation")
    ds_state = fields.Selection(selection=state, string="Observation")
    ds_responsible = fields.Char(string="Responsible")
    dsd_review = fields.Boolean(string="Budget review")


    def init(self):
        tools.drop_view_if_exists(self._cr, 'expenses_control_report')
        self._cr.execute("""
            CREATE or REPLACE view expenses_control_report AS (
            WITH refund_data AS (
                SELECT
                    dsd.id AS id,
                    dr.date AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' AS dr_date,
                    b.name AS dr_budget,
                    cc.name AS dr_cost_center,
                    cc.code AS dr_cc_code,
                    dr.card_payment AS dr_card_payment,
                    rp2.name AS dr_paid_to,
                    ds.requirement_id AS dr_name,
                    dr.amount_currency_type AS dr_currency,
                    COALESCE(CAST(dr.amount_soles AS numeric(10, 2)), CAST(dr.amount_uss AS numeric(10, 2))) AS dr_rounded_amount,
                    ds.name AS dr_settlement,
                    ds.create_date AT TIME ZONE 'UTC' AT TIME ZONE 'America/Lima' AS ds_date,
                    dsd.date AS dsd_date,
                    slp.name AS dsd_document_type,
                    dsd.document AS dsd_document,
                    dsd.reason AS dsd_reason,
                    dsd.amount AS dsd_amount,
                    ds.total_import AS ds_total_import,
                    CAST(dsd.igv_total AS numeric(10,2)) AS dsd_igv_total,
                    tt.name AS dsd_tax_perc,
                    CAST(dsd.base_amount_total AS numeric(10,2)) AS dsd_total_amount_base,
                    ds.state AS ds_state,
                    rp.name AS ds_responsible,
                    dsd.review_in_quotation AS dsd_review,
                    -- Nuevas columnas
                    CAST(CASE WHEN CAST(COALESCE(CAST(dr.amount_soles AS numeric(10, 2)), CAST(dr.amount_uss AS numeric(10, 2))) AS numeric) < ds.total_import
                        THEN ds.total_import - CAST(COALESCE(CAST(dr.amount_soles AS numeric(10, 2)), CAST(dr.amount_uss AS numeric(10, 2))) AS numeric)
                        ELSE 0
                    END AS numeric(10,2)) AS refund_employee,
                    CASE WHEN CAST(COALESCE(CAST(dr.amount_soles AS numeric(10, 2)), CAST(dr.amount_uss AS numeric(10, 2))) AS numeric) >= ds.total_import
                        THEN CAST(COALESCE(CAST(dr.amount_soles AS numeric(10, 2)), CAST(dr.amount_uss AS numeric(10, 2))) AS numeric) - ds.total_import
                        ELSE 0
                    END AS refund_mkt,
                    ROW_NUMBER() OVER (PARTITION BY ds.requirement_id ORDER BY dsd.date ASC) AS rn
                FROM documental_requirements AS dr
                    LEFT JOIN budget AS b ON b.id=dr.budget_id
                    LEFT JOIN res_partner AS rp2 ON rp2.id=dr.paid_to
                    LEFT JOIN cost_center AS cc ON cc.id=b.cost_center_id
                    LEFT JOIN res_users AS ru ON ru.id=dr.full_name
                    LEFT JOIN res_partner AS rp ON rp.id=ru.partner_id
                    LEFT JOIN documental_settlements AS ds ON dr.id=ds.requirement_id
                    LEFT JOIN documental_settlements_detail AS dsd ON ds.id=dsd.documental_settlement_id
                    LEFT JOIN tax_taxes AS tt ON tt.id=dsd.tax_igv_id
                    LEFT JOIN settlement_line_type AS slp ON slp.id=dsd.document_type
            )
            SELECT
                id,
                dr_date,
                dr_budget,
                dr_cost_center,
                dr_cc_code,
                dr_card_payment,
                dr_paid_to,
                dr_name,
                dr_currency,
                CASE WHEN rn = 1 THEN dr_rounded_amount ELSE 0.00 END AS dr_rounded_amount,
                dr_settlement,
                ds_date,
                dsd_date,
                dsd_document_type,
                dsd_document,
                dsd_reason,
                dsd_amount,
                ds_total_import,
                dsd_igv_total,
                dsd_tax_perc,
                dsd_total_amount_base,
                ds_state,
                ds_responsible,
                dsd_review,
                CASE WHEN rn = 1 THEN refund_employee ELSE 0 END AS refund_employee,
                CASE WHEN rn = 1 THEN refund_mkt ELSE 0.00 END AS refund_mkt
            FROM refund_data
            ORDER BY dr_date DESC, dsd_date ASC
            );
        """)