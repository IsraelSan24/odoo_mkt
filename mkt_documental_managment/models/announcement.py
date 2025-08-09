from odoo import models, fields

class Announcement(models.Model):
    _name = 'internal.announcement'
    _description = 'Internal Announcement'
    _order = 'date desc'

    name = fields.Char('Title', required=True)
    message = fields.Text('Message', required=True)
    date = fields.Datetime('Date', default=fields.Datetime.now)
    author_id = fields.Many2one('res.users', 'Author', default=lambda self: self.env.user)
    active = fields.Boolean('Active', default=True)
