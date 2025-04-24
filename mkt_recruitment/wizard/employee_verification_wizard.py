from odoo import models, fields

class EmployeeVerificationWizard(models.TransientModel):
    _name = 'employee.verification.wizard'
    _description = 'Wizard to display duplicate or missing employees'

    message = fields.Text(string="Message")

    def action_close(self):
        return {'type': 'ir.actions.act_window_close'}