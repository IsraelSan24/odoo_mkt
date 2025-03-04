from odoo import _, fields, models

class ResPartnerBrandEmployee(models.Model):
    _inherit = 'res.partner.brand'
    _description = 'A simple brand'

    for_province = fields.Boolean(default=False, string="For province")
    for_capital = fields.Boolean(default=False, string="for capital")
    employee_ids = fields.Many2many('hr.employee', 'hr_brand_employee_rel', 'brand_id', 'employee_id', string="Employes")