from odoo import _, api, fields, models

class RequirementServiceType(models.Model):
    _name = 'requirement.service.type'
    _description = 'Service Type in Requirements'
    _order = 'id desc'

    name = fields.Char(copy=False, string="Type Service", required=True)
    percentage = fields.Float(string="Percentage(%)", digits=(10,2))
    amount_from = fields.Float(string="Amount From")
    detraction = fields.Boolean(string="For detraction", default=True)
    retention = fields.Boolean(string="For retention", default=False)
    code = fields.Char(string="Code")