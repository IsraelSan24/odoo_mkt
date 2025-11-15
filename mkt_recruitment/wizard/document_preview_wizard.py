from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

class DocumentPreviewWizard(models.TransientModel):
    _name = 'document.preview.wizard'
    _description = 'Document Preview'

    partner_id = fields.Many2one('res.partner', string='Partner')
    document_field = fields.Char(string='Document Field Name')
    document_filename = fields.Char(string='Filename', readonly=True)
    previous_wizard_id = fields.Integer(string='Previous Wizard ID')
    previous_wizard_model = fields.Char(string='Previous Wizard Model')
    document_html = fields.Html(string='Document HTML', compute='_compute_document_html')
    document_base64 = fields.Char(string='Document Base64', compute='_compute_document_base64')

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
    
    @api.depends('partner_id', 'document_field')
    def _compute_document_base64(self):
        for record in self:
            if record.partner_id and record.document_field:
                record.partner_id.invalidate_cache([record.document_field])
                partner = self.env['res.partner'].with_context(bin_size=False).browse(record.partner_id.id)
                image_base64 = getattr(partner, record.document_field, False)
                
                if image_base64 and len(image_base64) > 10:
                    record.document_base64 = image_base64.decode('utf-8') if isinstance(image_base64, bytes) else image_base64
                else:
                    record.document_base64 = False
            else:
                record.document_base64 = False