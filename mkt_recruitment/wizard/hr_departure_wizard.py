# -*- coding: utf-8 -*-
from odoo.exceptions import UserError
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, _


class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    def action_departure_employees(self):
        employee = self.employee_id
        equipments = self.env['maintenance.equipment'].search([('employee_id','=','employee.id')])
        if equipments:
            raise UserError(_('This employee has devices assigned to him, please contact the systems area to have him reassigned.'))
        if self.env.context.get('toggle_active', False) and employee.active:
            employee.with_context(no_wizard=True).toggle_active()
        employee.departure_reason_id = self.departure_reason_id
        employee.departure_description = self.departure_description
        employee.departure_date = self.departure_date

        if employee.user_id:
            employee.user_id.toggle_active()
        if employee.address_home_id:
            employee.address_home_id.user_id.toggle_active()
            employee.address_home_id.is_validate = False
        #cesar siempre debe desvalidar
        