from odoo import models, fields

class DocumentPreviewWizard(models.TransientModel):
    _name = 'document.preview.wizard'
    _description = 'Document Preview'

    document = fields.Binary(string='Document', readonly=True)
    document_filename = fields.Char(string='Filename', readonly=True)
    previous_wizard_id = fields.Integer(string='Previous Wizard ID')
    previous_wizard_model = fields.Char(string='Previous Wizard Model')

    def action_go_back(self):
        self.ensure_one()
        applicant_id = self.env.context.get('active_id')
        partner_id = self.env.context.get('partner_id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'Regresar al Wizard Anterior',
            'res_model': self.previous_wizard_model,
            'res_id': self.previous_wizard_id,
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': applicant_id,
                'partner_id': partner_id,
            }
        }