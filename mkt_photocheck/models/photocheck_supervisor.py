from odoo import api, models, fields

class PhotocheckSupervisor(models.Model):
    _name = "photocheck.supervisor"
    _description = "Photocheck Supervisor"

    name = fields.Char(string='Name')
    user_id = fields.Many2one(comodel_name='res.users', string='Supervisor')
    brand_group_ids = fields.Many2many(comodel_name='photocheck.brand.group', string='Brand Groups')

    city_ids = fields.Many2many(
        comodel_name='photocheck.city',
        relation='photocheck_supervisor_city_rel',
        column1='supervisor_id',
        column2='city_id',
        string='Cities',
        default=lambda self: self._get_all_cities()
    )
    
    @api.model
    def _get_all_cities(self):
        """Retorna todas las ciudades por defecto"""
        return self.env['photocheck.city'].search([]).ids