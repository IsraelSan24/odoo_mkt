from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

states = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled')
    ]


class SpaceBooking(models.Model):
    _name = 'space.booking'
    _inherit = ['mail.thread']
    _description = 'Space reservation'

    name = fields.Char(string="Reservation", compute="_compute_name", store=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    room_id = fields.Many2one('space.room', string='Space', required=True)
    floor = fields.Integer(related='room_id.floor', string='Floor', store=True)
    room_name = fields.Char(related='room_id.name', string='Room name', store=True)
    room_capacity = fields.Integer(related='room_id.capacity', string='Room Capacity', store=True)
    start_datetime = fields.Datetime(string='Start', required=True)
    end_datetime = fields.Datetime(string='End', compute='_compute_end_datetime', store=True)
    duration = fields.Float(string='Duration (Hours)', default=1, required=True)
    item_ids = fields.Many2many(
        'space.booking.item',
        string="Additional Items",
        compute='_compute_item_ids',
        store=True
    )
    notes = fields.Text(string="Notes")
    state = fields.Selection(selection=states, default='draft')
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")

    full_name = fields.Char(
        string="Full Name", 
        compute="_compute_full_name", 
        store=True
    )

    @api.depends('user_id', 'first_name', 'last_name')
    def _compute_full_name(self):
        for record in self:
            if record.user_id:
                record.full_name = record.user_id.partner_id.name
            else:
                record.full_name = f"{record.first_name or ''} {record.last_name or ''}".strip()

    @api.depends('room_name')
    def _compute_name(self):
         for record in self:
             if record.room_name:
                 record.name = "Reservation room '%s'" % record.room_name
             else:
                 record.name = "Reservation"
    
    @api.depends('room_id.item_ids')
    def _compute_item_ids(self):
        for rec in self:
            rec.item_ids = rec.room_id.item_ids

    @api.depends('start_datetime', 'duration')
    def _compute_end_datetime(self):
        for record in self:
            if record.start_datetime and record.duration:
                record.end_datetime = record.start_datetime + timedelta(hours=record.duration)
            else:
                record.end_datetime = False


    @api.constrains('start_datetime', 'duration', 'room_id', 'quantity')
    def _check_availability(self):
        for record in self:
            conflicts = self.search([
                ('room_id', '=', record.room_id.id),
                ('start_datetime', '<', record.start_datetime + timedelta(hours=record.duration)),
                ('start_datetime', '>=', record.start_datetime),
                ('id', '!=', record.id),
                ('state', '!=', 'cancelled')
            ])
            if conflicts:
                raise ValidationError('The room is already reserved in this time frame.')


    @api.model
    def create(self, vals):
        vals['name'] = vals.get('name', _('Reservation #%s' % self.env['ir.sequence'].next_by_code('space.booking.sequence')))
        return super(SpaceBooking, self).create(vals)


    def action_request(self):
        for record in self:
            record.state = 'pending'
            record._notify_receptionist('Requested')


    def action_confirm(self):
        for record in self:
            record.state = 'confirmed'
            record._notify_user_and_superuser('Confirmed')


    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
            record._notify_user_and_superuser('Cancelled')


    def _notify_user_and_superuser(self, action):
        user = self.user_id
        system_users = self.env['res.users'].search([
            ('groups_id', 'in', [self.env.ref('base.group_system').id])
        ])
        users = [user] + list(system_users)
        
        # Obtener los nombres de los ítems relacionados con la reserva
        item_names = ', '.join(self.item_ids.mapped('name'))

        if users:
            notification_ids = [(0, 0, {
                'res_partner_id': user.partner_id.id,
                'notification_type': 'inbox'
            }) for user in users]
            self.env['mail.message'].create({
                'message_type': 'notification',
                'body': f'A room has been {action.lower()}: {self.room_name} with the item(s): {item_names}',
                'subject': f'Reservation {action}',
                'partner_ids': [(4, user.partner_id.id) for user in users],
                'model': self._name,
                'res_id': self.id,
                'notification_ids': notification_ids,
                'author_id': self.env.user.partner_id.id
            })


    def _notify_receptionist(self, action):
        receptionist_group = self.env.ref('mkt_roomreserves.group_receptionist')
        receptionists = self.env['res.users'].search([('groups_id', 'in', [receptionist_group.id])])
        if receptionists:
            notification_ids = [(0, 0, {
                'res_partner_id': user.partner_id.id,
                'notification_type': 'inbox'
            }) for user in receptionists]
            self.env['mail.message'].create({
                'message_type': 'notification',
                'body': f'A reservation request has been {action.lower()} for room: {self.room_name}.',
                'subject': f'Room Reservation {action}',
                'partner_ids': [(4, user.partner_id.id) for user in receptionists],
                'model': self._name,
                'res_id': self.id,
                'notification_ids': notification_ids,
                'author_id': self.env.user.partner_id.id
            })