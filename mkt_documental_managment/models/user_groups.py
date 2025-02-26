from odoo import _, fields, models

class UserGroups(models.Model):
    _name = 'user.groups'

    name = fields.Char(string='Name')
    reference = fields.Char(string='Reference')
    category = fields.Many2one(comodel_name='groups.categorys',string='Category')
    employee_ids = fields.Many2many('hr.employee', 'hr_group_employee_rel', 'group_id', 'employee_id', string='Employees')


    def action_user_group_from(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employees',
            'res_model': 'user.groups',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }