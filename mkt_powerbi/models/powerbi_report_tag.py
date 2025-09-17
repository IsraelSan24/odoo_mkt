from odoo import fields, models

class PowerBIReportTag(models.Model):
    _name = 'powerbi.report.tag'
    _description = 'Power BI report tags model'

    name = fields.Char(required=True)

