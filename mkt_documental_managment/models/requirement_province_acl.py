# -*- coding: utf-8 -*-
from odoo import api, fields, models

class RequirementProvinceACL(models.Model):
    _name = 'requirement.province.acl'
    _description = 'ACL - Provincias (No Lima) por empleado'
    _rec_name = 'employee_id'
    _order = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='Empleado', required=True, index=True)
    user_id = fields.Many2one('res.users', string='Usuario', related='employee_id.user_id', store=True, readonly=True)
    cost_center_ids = fields.Many2many('cost.center', 'req_prov_acl_cc_rel', 'acl_id', 'cc_id',
                                       string='Centros de Costo Permitidos', required=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('employee_unique', 'unique(employee_id)', 'Ya existe una asignación para este empleado.'),
    ]


class ResUsers(models.Model):
    _inherit = 'res.users'

    def get_provincial_cc_ids(self):
        """Devuelve ids de cost.center permitidos para el usuario según la ACL."""
        self.ensure_one()
        acls = self.env['requirement.province.acl'].sudo().search([
            ('user_id', '=', self.id),
            ('active', '=', True),
        ])
        return acls.mapped('cost_center_ids').ids or []
