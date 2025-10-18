# -*- coding: utf-8 -*-
from odoo import models, fields

class HrDepartureWizard(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    add_to_blacklist = fields.Boolean(
        string="Agregar a Blacklist",
        default=False,
        help="Si está marcado, el contacto del empleado quedará en la lista negra."
    )

    def action_register_departure(self):
        res = super().action_register_departure()
        for wiz in self:
            if wiz.add_to_blacklist and wiz.employee_id and wiz.employee_id.address_home_id:
                wiz.employee_id.address_home_id.blacklist = True
        return res
