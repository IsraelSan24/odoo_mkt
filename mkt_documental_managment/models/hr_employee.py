from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class HrEmployeeGroups(models.Model):
    _inherit = 'hr.employee'

    is_supervize_province = fields.Boolean(defatul=False, copy=False, string='Province to supervize')
    brand_ids = fields.Many2many('res.partner.brand', 'hr_brand_employee_rel', 'employee_id', 'brand_id', string="Brands")
    group_ids = fields.Many2many('user.groups', 'hr_group_employee_rel', 'employee_id', 'group_id', string="Groups")
    

    @api.onchange('brand_ids', 'group_ids', 'is_supervize_province')
    def _onchange_fields(self):
        _logger.info('\n\n\n ----------------------------------------------------_onchange_fields----------------------------------------------------: %s \n\n\n', '_onchange_fields')
        self.env['ir.rule'].clear_caches()

    @api.model
    def create(self, vals):
        res = super(HrEmployeeGroups, self).create(vals)
        _logger.info('\n\n\n ----------------------------------------------------create----------------------------------------------------: %s \n\n\n', 'create')
        self.env['ir.rule'].clear_caches()
        return res

    def write(self, vals):
        res = super(HrEmployeeGroups, self).write(vals)
        _logger.info('\n\n\n ----------------------------------------------------write----------------------------------------------------: %s \n\n\n', 'write')
        self.env['ir.rule'].clear_caches()
        return res

    def unlink(self):
        res = super(HrEmployeeGroups, self).unlink()
        _logger.info('\n\n\n ----------------------------------------------------unlink----------------------------------------------------: %s \n\n\n', 'unlink')
        self.env['ir.rule'].clear_caches()
        return res