from odoo import _, fields, models

class HrEmployeePrivate(models.Model):
    _inherit = 'hr.employee'
    
    def action_view_paycheck(self):
        paycheck = self.env['paycheck'].search([('employee_id','=',self.id)])
        open_view_paycheck = {
            'name': _('Paychecks'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'paycheck',
            'type': 'ir.actions.act_window',
            'domain': [('id','in',paycheck.ids)]
        }
        return open_view_paycheck