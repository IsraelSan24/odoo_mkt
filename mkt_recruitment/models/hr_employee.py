from odoo import _, fields, models

class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'

    cost_center_id = fields.Many2one(comodel_name='cost.center', string='Cost center')
    partner_brand_id = fields.Many2one(related='cost_center_id.partner_brand_id', string='Brand')
    is_back_office = fields.Boolean(default=False, string='Back Office')