from odoo import models, fields, api, _

class IdentifiersWizard(models.TransientModel):
    _name = 'contract.mass.identifiers.wizard'
    _description = 'Wizard to paste identifiers for mass contract processing'

    identifiers_input = fields.Text(
        string="Identifiers (one per line or comma separated)",
        help="Paste one identifier per line or separate them by commas/semicolons.",
    )
    not_found_identifiers = fields.Text(string="Identifiers not found", readonly=True)

    def action_apply(self):
        """Escribimos el texto en el registro principal y llamamos al procesador."""
        self.ensure_one()
        # recuperar el registro principal desde el contexto
        model = self._context.get('active_model')
        res_id = self._context.get('active_id')

        if not model or not res_id:
            return {'type': 'ir.actions.act_window_close'}

        main_rec = self.env[model].browse(res_id)

        # Logic for renovation mode
        if self._context.get('mode') == 'renovation':
            if hasattr(main_rec, 'process_identifiers_renovation'):
                missing = main_rec.process_identifiers_renovation(self.identifiers_input)
                if missing:
                    self.not_found_identifiers = '\n'.join(missing)
                    return {
                        'type': 'ir.actions.act_window',
                        'res_model': 'contract.mass.identifiers.wizard',
                        'view_mode': 'form',
                        'res_id': self.id,
                        'view_id': self.env.ref('mkt_recruitment.identifiers_wizard_form_view').id,
                        'target': 'new',
                        'context': self._context
                    }
                else:
                    return {'type': 'ir.actions.act_window_close'}

        # Guardar el texto (si tienes un campo identifiers_input en el modelo principal)
        main_rec.sudo().write({
            'identifiers_input': self.identifiers_input or ''
        })

        # Llamar a la lógica que procesa los identificadores. 
        if hasattr(main_rec, 'process_identifiers'):
            result = main_rec.process_identifiers()

            return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Import finished'),
                        'message': result['message'],
                        'type': result['type_message'],
                        'sticky': True,
                        'next': {'type': 'ir.actions.act_window_close'} ,
                    }
                }