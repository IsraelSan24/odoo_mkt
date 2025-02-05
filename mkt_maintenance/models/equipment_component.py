from odoo import fields, models, api

components = [
    ('screen', 'Screen'),
    ('keyboard', 'Keyboard'),
    ('battery', 'Battery'),
    ('charger', 'Charger'),
    ('wifi', 'Wi-Fi'),
    ('casing', 'Casing'),
    ('touchpad', 'Touchpad'),
    ('ports', 'Ports'),
]
conditions = [
    ('good', 'Good'), 
    ('bad', 'Bad'),
]

class EquipmentComponent(models.Model):
    _name = 'equipment.component'
    _description = 'Equipment Component'

    component_name = fields.Selection(selection=components, string='Component', default='screen', required=True)
    condition = fields.Selection(selection=conditions, string="Condition", required=True, default='good')
    observation = fields.Char(string="Observation")
    status_id = fields.Many2one(comodel_name='equipment.status', string='Status Report')