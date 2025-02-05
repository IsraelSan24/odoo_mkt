from odoo import models, fields

class SpaceBookingItem(models.Model):
    _name = 'space.booking.item'
    _description = 'Reserve Item'

    name = fields.Char(string='Item', required=True, store=True)
    stock = fields.Integer(string='Stock', store=True)
    booking_id = fields.Many2one('space.booking')