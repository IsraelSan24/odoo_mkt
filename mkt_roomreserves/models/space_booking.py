from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta

states = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('finished', 'Finished')
    ]


class SpaceBooking(models.Model):
    _name = 'space.booking'
    _inherit = ["mail.thread", "mail.activity.mixin"]
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
    state = fields.Selection(selection=states, default='draft', tracking=True)
    first_name = fields.Char(string="First Name")
    last_name = fields.Char(string="Last Name")

    full_name = fields.Char(
        string="Full Name",
        default=lambda self: self._default_full_name(),
        store=True
    )

    contact = fields.Char(string="Contact")

    is_receptionist = fields.Boolean(
        compute='_compute_is_receptionist',
        store=False
    )


    @api.depends()
    def _compute_is_receptionist(self):
        for record in self:
            record.is_receptionist = self.env.user.has_group('mkt_roomreserves.group_receptionist')


    def _default_full_name(self):
        first_name = self.env.user.partner_id.name.split()[0] if self.env.user.partner_id.name else ''
        last_name = " ".join(self.env.user.partner_id.name.split()[1:]) if self.env.user.partner_id.name else ''
        return f"{first_name} {last_name}".strip() if first_name or last_name else ''


    @api.depends('full_name', 'room_name')
    def _compute_name(self):
        for record in self:
            full_name = record.full_name or ""
            room_name = record.room_name or ""
            record.name = f"{full_name} - {room_name}"
    

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
        subject = f'Reservation {action}'
        body = f'''
            <p>Your reservation has been <b>{action.lower()}</b> for {self.room_name} at {self.start_datetime}.</p>
            <p>Item(s): {item_names}</p>
        '''

        # Usar login en lugar de email
        email_users = [u for u in users if u.login and '@' in u.login]

        if email_users:
            email_to = ','.join([u.login for u in email_users])
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': email_to,
                'email_from': self.env.user.login or 'no-reply@example.com',
            }
            self.env['mail.mail'].create(mail_values).send()


    def _notify_receptionist(self, action):
        receptionist_group = self.env.ref('mkt_roomreserves.group_receptionist')
        receptionists = self.env['res.users'].search([('groups_id', 'in', [receptionist_group.id])])

        subject = f'Room Reservation {action}'
        body = f'''
            <p>A reservation request has been <b>{action.lower()}</b> for room {self.room_name} by {self.full_name}.</p>
        '''

        # Usar login en lugar de email
        email_receptionists = [r for r in receptionists if r.login and '@' in r.login]

        if email_receptionists:
            email_to = ','.join([r.login for r in email_receptionists])
            mail_values = {
                'subject': subject,
                'body_html': body,
                'email_to': email_to,
                'email_from': self.env.user.login or 'no-reply@example.com',
            }
            self.env['mail.mail'].create(mail_values).send()

    @api.model
    def _cron_auto_finish_reservations(self):
        """ Cambia automáticamente a 'finished' las reservas que hayan terminado hace más de un día """
        today = fields.Datetime.now()
        one_day_ago = today - timedelta(days=1)

        bookings_to_finish = self.search([
            ('end_datetime', '<=', one_day_ago),
            ('state', '=', 'confirmed')
        ])

        for booking in bookings_to_finish:
            booking.state = 'finished'
            booking._notify_user_and_superuser('Finished')