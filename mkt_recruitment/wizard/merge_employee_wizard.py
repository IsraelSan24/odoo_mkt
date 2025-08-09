from odoo import models, fields, api, _
import logging

_logger = logging.getLogger(__name__)

class MergeEmployeeWizard(models.TransientModel):
    _name = 'merge.employee.wizard'
    _description = 'Merge partner records'

    destination_id = fields.Many2one(comodel_name='hr.employee', string="Destiny record", required=True, domain=lambda self: self.env.context.get('destination_domain', []))
    source_id = fields.Many2one('hr.employee', string='Merge Record')
    employee_ids = fields.Many2many('hr.employee')


    # _logger.info('\n\n\n --------------------------onChange01--------------------------: %s \n\n\n', 1)
    @api.onchange('destination_id')
    def on_change_source(self):
        self.employee_ids = self.env.context.get('active_ids', [])
        active_ids = self.env.context.get('active_ids', [])
        if self.destination_id.id == active_ids[0]:
            self.source_id = active_ids[1]
        elif self.destination_id.id == active_ids[1]:
            self.source_id = active_ids[0]


    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_ids = self.env.context.get('active_ids', [])
        if len(active_ids) != 2:
            raise ValueError(_("You must select exactly 2 records in order to merge them."))
        self = self.with_context(destination_domain=[('id', 'in', active_ids)])
        return res

    def action_merge(self):
        active_ids = self.env.context.get('active_ids', [])
        if self.destination_id.id == active_ids[0]:
            self.source_id = active_ids[1]
        elif self.destination_id.id == active_ids[1]:
            self.source_id = active_ids[0]
        user_id_dict = {}
        dest = self.destination_id
        src = self.source_id

        for field_name in dest._fields:
            if field_name in ['id', 'create_uid', 'create_date', 'write_uid', 'write_date', 'user_id']:
                continue
            val_dest = getattr(dest, field_name)
            val_src = getattr(src, field_name)

            if not val_dest and val_src:
                setattr(dest, field_name, val_src)

        if hasattr(src, 'user_id'):
            user_id_dict['user_id'] = getattr(src, 'user_id')

        src.unlink()

        if 'user_id' in user_id_dict and not dest.user_id:
            setattr(dest, 'user_id', user_id_dict['user_id'])

        return {'type': 'ir.actions.act_window_close'}
