from odoo import _, api, fields, models
from odoo.addons.mkt_photocheck.models.api_dni import apiperu_dni
import rembg
import numpy as np
from PIL import Image
import base64
import io
from babel.dates import format_datetime
from odoo.http import request

state = [
    ('draft','Draft'),
    ('to_do','To Do'),
    ('done','Done'),
    ('refused','Refused')
]

duplicates = [
    ('new','New'),
    ('duplicate','Duplicate')
]

class Photocheck(models.Model):
    _name = 'photocheck'
    _description = 'Photocheck'
    _inherit = ['mail.thread','mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(required=True, default=lambda self:_('New'), string='Name')
    first_name = fields.Char(required=True, string='First Name')
    initial_name = fields.Char(compute='compute_initial_name', string='Initial Name')
    last_name = fields.Char(required=True, string='Last Name')
    state = fields.Selection(selection=state, default='draft', string='State')
    state_duplicate = fields.Selection(selection=duplicates, default='new', string='State Duplicate')
    photo_raw = fields.Image(string='Photo')
    photo = fields.Image()
    photo_name = fields.Char(compute='compute_photo_name', store=True)
    user_id = fields.Many2one(comodel_name='res.users', default=lambda self: self.env.user, string='User')
    brand_counter = fields.Integer(compute='compute_brand_counter', string='Brand Counter')
    brand_ids = fields.Many2many(comodel_name='res.partner.brand', string='Brand', compute='compute_brands')
    photocheck_brand_group_id = fields.Many2one(comodel_name='photocheck.brand.group', string='Brand Group')
    dni = fields.Char(required=True, string='DNI')
    job_id = fields.Many2one(comodel_name='photocheck.job', string='Job')
    complete_name = fields.Char(string='Complete Name')
    request_date =  fields.Datetime(string='Request Date')
    done_date =  fields.Datetime(string='Done Date')
    refused_date =  fields.Datetime(string='Refused Date')
    note = fields.Text('Note', translate=True)
    photocheck_supervisor_id = fields.Many2one(comodel_name='photocheck.supervisor', string='Supervisor')
    active = fields.Boolean(string='Active', default=True, tracking=True)

    # generar 2 registros mas para cada estado
    email_status_change_send_on = fields.Datetime('Status Change Email Sent On')

    def get_photocheck_url(self):
        """
        Este método genera la URL completa para redirigir a la vista de formulario,
        utilizando una URL base dinámica.
        """
        for record in self:
            base_url = request.httprequest.host_url  # Obtiene la URL base dinámica
            params = {
                'id': record.id,
                'model': 'photocheck',
                'view_type': 'form',
            }
            # query_string = "&".join([f"{key}={value}" for key, value in params.items()])
            query_string = 'id=%s&model=%s&view_type=form' % (record.id,'photocheck')
            return f'{base_url}web#{query_string}'


    @api.depends('photocheck_brand_group_id')
    def compute_brands(self):
        for rec in self:
            rec.brand_ids = [(6,0,rec.photocheck_brand_group_id.brand_ids.ids)]  


    @api.depends('first_name')
    def compute_initial_name(self):
        for record in self:
            if record.first_name:
                parts = record.first_name.split()
                record.initial_name = parts[0] if parts else ''
            else:
                record.initial_name = ''


    @api.depends('dni','complete_name')
    def compute_photo_name(self):
        for red in self:
            if red.photo_raw:
                if red.dni and red.complete_name:
                    red.photo_name = red.dni + '_' + red.complete_name


    @api.depends('brand_ids')
    def compute_brand_counter(self):
        self.brand_counter = len(self.brand_ids)


    @api.onchange('dni')
    def onchange_complete_name(self):
        for record in self:
            if record.dni:
                try:
                    complete_name = apiperu_dni(record.dni)[0]
                    first_name = apiperu_dni(record.dni)[1]
                    father_last_name = apiperu_dni(record.dni)[2]
                    mother_last_name = apiperu_dni(record.dni)[3]
                    record.complete_name = complete_name
                    record.first_name = first_name
                    record.last_name = father_last_name + ' ' + mother_last_name
                except:
                    pass


    def modify_image(self):
        photo_data = base64.b64decode(self.photo)
        input_array = np.array(Image.open(io.BytesIO(photo_data)))
        output_array = rembg.remove(input_array)
        output_image = Image.fromarray(output_array)
        output_data = io.BytesIO()
        output_image.save(output_data, format='PNG')
        self.photo = base64.b64encode(output_data.getvalue())


    def button_to_do(self):
        self.write({
            'state': 'to_do',
            'request_date': format_datetime(fields.Datetime.now(), format='yyyy-MM-dd HH:mm:ss', locale='es_PE'),
        })
        self.send_email_status_change()


    def button_draft(self):
        self.state = 'draft'


    def button_done(self):
        self.write({
            'state': 'done',
            'done_date': format_datetime(fields.Datetime.now(), format='yyyy-MM-dd HH:mm:ss', locale='es_PE'),
        })
        self.send_email_done()


    def button_refused(self):
        self.write({
            'state': 'refused',
            'refused_date': format_datetime(fields.Datetime.now(), format='yyyy-MM-dd HH:mm:ss', locale='es_PE'),
        })
        self.send_email_refused()


    def send_email_status_change(self):
        self.ensure_one()
        template = self.env.ref('mkt_photocheck.mail_template_photocheck_status_change')
        template.sudo().send_mail(self.id, force_send=True)
        self.sudo().write({
            'email_status_change_send_on': fields.Datetime.now()
        })
        self.sudo().message_post(
            body=_(
                'The email to communicate the photocheck status change to %s was sent to %s at %s.'
            ) % (
                self.state,
                'fotocheck@marketing-alterno.com',
                self.email_status_change_send_on
            )
        )


    def send_email_refused(self):
        self.ensure_one()
        template = self.env.ref('mkt_photocheck.mail_template_photocheck_refused')
        template.sudo().send_mail(self.id, force_send=True)
        self.sudo().write({
            'email_status_change_send_on': fields.Datetime.now()
        })
        self.sudo().message_post(
            body=_(
                'The email to communicate the photocheck was refused to %s was sent to %s(%s) at %s.'
            ) % (
                self.state,
                self.photocheck_supervisor_id.user_id.partner_id.name,
                self.photocheck_supervisor_id.user_id.partner_id.email,
                self.email_status_change_send_on
            )
        )

 
    def send_email_done(self):
        self.ensure_one()
        template = self.env.ref('mkt_photocheck.mail_template_photocheck_done')
        template.sudo().send_mail(self.id, force_send=True)
        self.sudo().write({
            'email_status_change_send_on': fields.Datetime.now()
        })
        self.sudo().message_post(
            body=_(
                'The email to communicate the photocheck was done to %s was sent to %s(%s) at %s.'
            ) % (
                self.state,
                self.photocheck_supervisor_id.user_id.partner_id.name,
                self.photocheck_supervisor_id.user_id.partner_id.email,
                self.email_status_change_send_on
            )
        )
       

    @api.model
    def create(self, vals):
        records = self.env['photocheck'].sudo().search([('dni','=',vals.get('dni','')),('state','!=','refused'),('active','=',True)])
        if records:
            vals['state_duplicate'] = 'duplicate'
        if vals.get('name',_('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('photocheck') or _('New')
        return super(Photocheck, self).create(vals)