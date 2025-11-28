from odoo import models, fields, api

class Locations(models.Model):
    _name = 'hr.attendance.geolocation.location'
    _description = 'Location'

    name = fields.Char(string='Name', required=True)
    longitude = fields.Float(string='Longitude', digits= (10, 8), required=True)
    latitude = fields.Float(string='Latitude', digits= (11, 8), required=True)
    proximity_radius = fields.Float(string='Proximity Radius', required=True)
    code = fields.Char(string='Code', compute='_compute_code', store=True)
    map_widget_field = fields.Float(string="Map Location", compute='_compute_map_widget_field', readonly=False, store=False)

    @api.depends('latitude')
    def _compute_map_widget_field(self):
        for record in self:
            record.map_widget_field = record.latitude

    @api.depends('name', 'proximity_radius')
    def _compute_code(self):
        for record in self:
            record.code = f"{record.name}_{record.proximity_radius}"