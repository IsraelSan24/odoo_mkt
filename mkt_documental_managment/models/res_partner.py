from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    deduction_bank = fields.Many2one(comodel_name="res.bank", string="Bank")
    deduction_acc_number = fields.Char(string="Account Number")
    province_id = fields.Many2one(comodel_name="res.province", string="Assigned Province", store=True)
    alias_name = fields.Char(string='Alias name')
    blacklist = fields.Boolean(default=False, string='Blacklist')