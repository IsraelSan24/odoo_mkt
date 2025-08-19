from odoo import models, fields, api, _

class IdentifiersWizard(models.TransientModel):
    _name = 'contract.mass.identifiers.wizard'
    _description = 'Wizard to paste identifiers for mass contract processing'

    identifiers_input = fields.Text(
        string="Identifiers (one per line or comma separated)",
        help="Paste one identifier per line or separate them by commas/semicolons.",
    )

    def action_apply(self):
        """Escribimos el texto en el registro principal y llamamos al procesador."""
        self.ensure_one()
        # recuperar el registro principal desde el contexto
        model = self._context.get('active_model')
        res_id = self._context.get('active_id')

        if not model or not res_id:
            return {'type': 'ir.actions.act_window_close'}

        main_rec = self.env[model].browse(res_id)
        # Guardar el texto (si tienes un campo identifiers_input en el modelo principal)
        main_rec.sudo().write({
            'identifiers_input': self.identifiers_input or ''
        })

        # Llamar a la lógica que procesa los identificadores. 
        if hasattr(main_rec, 'process_identifiers'):
            main_rec.process_identifiers()

        # # cerrar modal
        # self.identifiers_input = ''  # Limpiar el campo de entrada
        return {'type': 'ir.actions.act_window_close'}
    
    
