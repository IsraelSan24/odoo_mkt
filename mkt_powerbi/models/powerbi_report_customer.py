from odoo import fields, models

class PowerBIReportCustomer(models.Model):
    _name = 'powerbi.report.customer'
    _description = "Power BI Report model for customers"

    powerbi_report_id = fields.Many2one(comodel_name='powerbi.report', string="Power BI Report", ondelete="cascade")
    customer_email = fields.Char(string="Email", related='user_id.partner_id.email', readonly=False, store=False)
    # From user we can get the partner information
    user_id = fields.Many2one(comodel_name="res.users",
                                 string="Customer",
                                 required=False,
                                 ondelete='cascade')