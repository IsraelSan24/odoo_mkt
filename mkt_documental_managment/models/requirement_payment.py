from odoo import _, fields, models

class RequirementPayment(models.Model):
    _name = 'requirement.payment'
    _description = 'Requirement payment'

    requirement_id = fields.Many2one(comodel_name='documental.requirements', string='Requirement')
    check_or_operation = fields.Selection(selection=[('check','Check'),('operation','Operation')], default='operation', string='Check/Operation')
    operation_number = fields.Char(string='Operation number')
    payment_date = fields.Date(required=True, string='Payment date')
    requirement_payroll_id = fields.Many2one(comodel_name='requirement.payroll', string='Payroll')
    amount = fields.Float(string='Amount')
