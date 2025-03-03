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
    is_province = fields.Boolean(string='Blacklist', compute="compute_is_province", store=True)

    @api.depends('province_id')
    def compute_is_province(self):
        for rec in self:
            rec.is_province = rec.province_id.name != 'Lima'