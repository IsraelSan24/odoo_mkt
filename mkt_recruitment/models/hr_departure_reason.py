from odoo import _, api, fields, models
from odoo.exceptions import UserError

class HrDepartureReason(models.Model):
    _inherit = 'hr.departure.reason'

    motive_number = fields.Integer(string='Motive number')