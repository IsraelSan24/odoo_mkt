from odoo import _, api, fields, models
from babel.dates import format_date
import user_agents
import random
import string
from geopy.geocoders import Nominatim
import logging
_logger = logging.getLogger(__name__)

relationship = [
    ('Madre','Mother'),
    ('Padre','Father'),
    ('Hermano','Brother'),
    ('Hermana','Sister'),
    ('Esposo/a','Spouse'),
    ('Conviviente','Concubine'),
    ('Hijo','Son'),
    ('Hija','Daughter'),
]

genders = [
    ('male', 'Male'),
    ('female', 'Female'),
]

state = [('draft','Draft'),
         ('to_sign','To Sign'),
         ('signed','Signed'),
         ('cancelled','Cancelled'),]

class RecruitmentDocument(models.Model):
    _name = 'recruitment.document'
    _inherit = ['portal.mixin','mail.thread','mail.activity.mixin','utm.mixin']
    _description = 'Recruitment documents as an affidavit'
    _order = 'id desc'


    name = fields.Char(copy=False, required=True, readonly=True, default=lambda self:_('New'))
    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")
    date_document = fields.Datetime(string="Document Date",
                                    required=True, readonly=True, copy=False,
                                    states={'draft': [('readonly',False)], 'to_sign': [('readonly', False)]},
                                    default=fields.Datetime.now)
    user_id = fields.Many2one(comodel_name="res.users", string="Responsible", default=lambda self:self.env.user)
    state = fields.Selection(string="State", selection=state, readonly=True, default='draft', tracking=True)
    applicant_signature = fields.Image(string="Signature", copy=False, attachment=True)
    signed_by = fields.Char(string='Signed by', copy=False)
    signed_on = fields.Datetime(string="Signed On", copy=False)
    signed_on_month = fields.Char(compute='_compute_signed_on_month', store=True)
    email_send_on = fields.Datetime(string='Email send at', copy=False)
    active = fields.Boolean(string='Active', default=True, tracking=True)

    partner_name = fields.Char(string='Name')
    email = fields.Char(string='Email')
    vat = fields.Char(string='Vat')
    street = fields.Char(string='Street')
    district = fields.Char(string='District')
    province = fields.Char(string='Province')
    department = fields.Char(string='Department')
    emergency_contact = fields.Char(string='Emergency contact')
    emergency_phone = fields.Char(string='Emergency phone')
    birthday = fields.Char(string='Birthday')
    phone = fields.Char(string='Phone')
    company = fields.Char(string='Company')
    company_department = fields.Char(string='Company department')
    company_vat = fields.Char(string='Company vat')
    gender = fields.Selection(selection=genders)

    familiar_dni1 = fields.Char()
    familiar_dni2 = fields.Char()
    familiar_dni3 = fields.Char()
    familiar_dni4 = fields.Char()
    familiar_dni5 = fields.Char()
    familiar_dni6 = fields.Char()
    familiar_dni7 = fields.Char()
    familiar_dni8 = fields.Char()
    familiar_dni9 = fields.Char()
    familiar_dni10 = fields.Char()
    
    familiar_full_name1 = fields.Char()
    familiar_full_name2 = fields.Char()
    familiar_full_name3 = fields.Char()
    familiar_full_name4 = fields.Char()
    familiar_full_name5 = fields.Char()
    familiar_full_name6 = fields.Char()
    familiar_full_name7 = fields.Char()
    familiar_full_name8 = fields.Char()
    familiar_full_name9 = fields.Char()
    familiar_full_name10 = fields.Char()

    familiar_birthday1 = fields.Date()
    familiar_birthday2 = fields.Date()
    familiar_birthday3 = fields.Date()
    familiar_birthday4 = fields.Date()
    familiar_birthday5 = fields.Date()
    familiar_birthday6 = fields.Date()
    familiar_birthday7 = fields.Date()
    familiar_birthday8 = fields.Date()
    familiar_birthday9 = fields.Date()
    familiar_birthday10 = fields.Date()

    familiar_relationship1 = fields.Selection(selection=relationship)
    familiar_relationship2 = fields.Selection(selection=relationship)
    familiar_relationship3 = fields.Selection(selection=relationship)
    familiar_relationship4 = fields.Selection(selection=relationship)
    familiar_relationship5 = fields.Selection(selection=relationship)
    familiar_relationship6 = fields.Selection(selection=relationship)
    familiar_relationship7 = fields.Selection(selection=relationship)
    familiar_relationship8 = fields.Selection(selection=relationship)
    familiar_relationship9 = fields.Selection(selection=relationship)
    familiar_relationship10 = fields.Selection(selection=relationship)

    familiar_gender1 = fields.Selection(selection=genders)
    familiar_gender2 = fields.Selection(selection=genders)
    familiar_gender3 = fields.Selection(selection=genders)
    familiar_gender4 = fields.Selection(selection=genders)
    familiar_gender5 = fields.Selection(selection=genders)
    familiar_gender6 = fields.Selection(selection=genders)
    familiar_gender7 = fields.Selection(selection=genders)
    familiar_gender8 = fields.Selection(selection=genders)
    familiar_gender9 = fields.Selection(selection=genders)
    familiar_gender10 = fields.Selection(selection=genders)

    familiar_address1 = fields.Char()
    familiar_address2 = fields.Char()
    familiar_address3 = fields.Char()
    familiar_address4 = fields.Char()
    familiar_address5 = fields.Char()
    familiar_address6 = fields.Char()
    familiar_address7 = fields.Char()
    familiar_address8 = fields.Char()
    familiar_address9 = fields.Char()
    familiar_address10 = fields.Char()

    is_beneficiary1 = fields.Boolean(default=True, string='Is Beneficiary?')
    is_beneficiary2 = fields.Boolean(default=True, string='Is Beneficiary?')
    is_beneficiary3 = fields.Boolean(default=True, string='Is Beneficiary?')
    is_beneficiary4 = fields.Boolean(default=True, string='Is Beneficiary?')
    is_beneficiary5 = fields.Boolean(default=True, string='Is Beneficiary?')
    is_beneficiary6 = fields.Boolean(default=True, string='Is Beneficiary?')
    is_beneficiary7 = fields.Boolean(default=True, string='Is Beneficiary?')
    is_beneficiary8 = fields.Boolean(default=True, string='Is Beneficiary?')
    is_beneficiary9 = fields.Boolean(default=True, string='Is Beneficiary?')
    is_beneficiary10 = fields.Boolean(default=True, string='Is Beneficiary?')

    identification_type = fields.Char()
    private_pension_system = fields.Boolean()
    afp_first_job = fields.Boolean()
    coming_from_onp = fields.Boolean()
    national_pension_system = fields.Boolean()

    job = fields.Char()

    validation_password = fields.Char(string='Validation password', copy=False)
    
    latitude = fields.Char(copy=False)
    longitude = fields.Char(copy=False)
    location_maps = fields.Char(copy=False)
    ip = fields.Char(copy=False)
    user_agents = fields.Char(copy=False)
    device_info = fields.Char(copy=False)
    device = fields.Char(copy=False)
    os = fields.Char(copy=False)
    browser = fields.Char(copy=False)


    def action_validation_password(self, enteredcode):
        self = self.sudo()
        return ( enteredcode == self.validation_password ) and self.state in ('draft','to_sign') and not self.applicant_signature


    def send_email_to_validate_document(self):
        self = self.sudo()
        self.validation_password = ''.join(random.choice(string.digits) for i in range(4))
        _logger.info('\n\n\n  self.validation_password: %s  \n\n\n', self.validation_password)
        mail_obj = self.env['mail.mail'].sudo()
        subject = 'Validation code of Marketing Alterno documents'
        body = '''
            Hola, tu código de verificación parar firmar tus documentos es el siguiente:\n
            %s
        ''' % ( self.validation_password )
        email_to = self.sudo().email
        _logger.info('\n\n\n  email_to: %s  \n\n\n', email_to)
        mail = mail_obj.create({
            'subject': subject,
            'body_html': body,
            'email_to': email_to,
        })
        mail.send()


    def geolocation(self, latitude, longitude, ip, user_agent):
        self = self.sudo()
        self.ensure_one()
        geolocator = Nominatim(user_agent='my-app')
        location = geolocator.reverse(str(latitude) + ', ' + str(longitude))
        self.latitude = latitude
        self.longitude = longitude
        self.ip = ip
        self.user_agents = user_agent
        ua = user_agents.parse(user_agent)
        device_info = f'{ua.device.family} / {ua.os.family} {ua.os.version_string} / {ua.browser.family} {ua.browser.version_string}'
        device = str(ua).split('/')[0]
        self.device_info = ua
        self.location_maps = 'https://www.google.com/maps/place/' + location.address
        self.device = device
        self.os = ua.os.family
        self.browser = ua.browser.family
        _logger.info('\n\n\n self.location_maps: %s \n\n\n', self.location_maps)


    @api.depends('signed_on')
    def _compute_signed_on_month(self):
        for rec in self:
            if rec.signed_on:
                rec.signed_on_month = format_date(rec.signed_on, format='MMMM', locale='es_PE')
            else:
                rec.signed_on = ''


    def send_email_to_employee_signed(self):
        template = self.env.ref('mkt_recruitment.mail_recruitment_document_signed')
        for rec in self:
            template.send_mail(rec.id, force_send=True)
            rec.write({'email_send_on': fields.Datetime.now()})
            rec.message_post(
                body = _('The email to inform that the files have been signed has been sent to %s ( %s ) at %s.') % ( rec.partner_id.name, rec.partner_id.personal_email, rec.email_send_on)
            )


    def refuse(self):
        self.state = 'cancelled'
        self.applicant_signature = False
        self.signed_by = False
        self.signed_on = False


    def send_to_sign(self):
            self.state = 'to_sign'


    def write_data(self):
        for rec in self:
            if rec.partner_id:
                rec.sudo().write({
                    'partner_name': rec.partner_id.name,
                    'email': rec.partner_id.personal_email,
                    'vat': rec.partner_id.vat,
                    'street': rec.partner_id.street,
                    'district': rec.partner_id.l10n_pe_district.name,
                    'province': rec.partner_id.city_id.name,
                    'department': rec.partner_id.state_id.name,
                    'emergency_contact': rec.partner_id.emergency_contact,
                    'emergency_phone': rec.partner_id.emergency_phone,
                    'birthday': rec.partner_id.birthday,
                    'phone': rec.partner_id.phone,
                    'company': rec.env.user.company_id.name,
                    'company_department': rec.env.user.company_id.state_id.name,
                    'company_vat': rec.env.user.company_id.vat,
                    'gender': rec.partner_id.gender,
                    'familiar_dni1': rec.partner_id.familiar_dni1,
                    'familiar_dni2': rec.partner_id.familiar_dni2,
                    'familiar_dni3': rec.partner_id.familiar_dni3,
                    'familiar_dni4': rec.partner_id.familiar_dni4,
                    'familiar_dni5': rec.partner_id.familiar_dni5,
                    'familiar_dni6': rec.partner_id.familiar_dni6,
                    'familiar_dni7': rec.partner_id.familiar_dni7,
                    'familiar_dni8': rec.partner_id.familiar_dni8,
                    'familiar_dni9': rec.partner_id.familiar_dni9,
                    'familiar_dni10': rec.partner_id.familiar_dni10,
                    'familiar_full_name1': rec.partner_id.familiar_full_name1,
                    'familiar_full_name2': rec.partner_id.familiar_full_name2,
                    'familiar_full_name3': rec.partner_id.familiar_full_name3,
                    'familiar_full_name4': rec.partner_id.familiar_full_name4,
                    'familiar_full_name5': rec.partner_id.familiar_full_name5,
                    'familiar_full_name6': rec.partner_id.familiar_full_name6,
                    'familiar_full_name7': rec.partner_id.familiar_full_name7,
                    'familiar_full_name8': rec.partner_id.familiar_full_name8,
                    'familiar_full_name9': rec.partner_id.familiar_full_name9,
                    'familiar_full_name10': rec.partner_id.familiar_full_name10,
                    'familiar_birthday1': rec.partner_id.familiar_birthday1,
                    'familiar_birthday2': rec.partner_id.familiar_birthday2,
                    'familiar_birthday3': rec.partner_id.familiar_birthday3,
                    'familiar_birthday4': rec.partner_id.familiar_birthday4,
                    'familiar_birthday5': rec.partner_id.familiar_birthday5,
                    'familiar_birthday6': rec.partner_id.familiar_birthday6,
                    'familiar_birthday7': rec.partner_id.familiar_birthday7,
                    'familiar_birthday8': rec.partner_id.familiar_birthday8,
                    'familiar_birthday9': rec.partner_id.familiar_birthday9,
                    'familiar_birthday10': rec.partner_id.familiar_birthday10,
                    'familiar_relationship1': rec.partner_id.familiar_relationship1,
                    'familiar_relationship2': rec.partner_id.familiar_relationship2,
                    'familiar_relationship3': rec.partner_id.familiar_relationship3,
                    'familiar_relationship4': rec.partner_id.familiar_relationship4,
                    'familiar_relationship5': rec.partner_id.familiar_relationship5,
                    'familiar_relationship6': rec.partner_id.familiar_relationship6,
                    'familiar_relationship7': rec.partner_id.familiar_relationship7,
                    'familiar_relationship8': rec.partner_id.familiar_relationship8,
                    'familiar_relationship9': rec.partner_id.familiar_relationship9,
                    'familiar_relationship10': rec.partner_id.familiar_relationship10,
                    'familiar_gender1': rec.partner_id.familiar_gender1,
                    'familiar_gender2': rec.partner_id.familiar_gender2,
                    'familiar_gender3': rec.partner_id.familiar_gender3,
                    'familiar_gender4': rec.partner_id.familiar_gender4,
                    'familiar_gender5': rec.partner_id.familiar_gender5,
                    'familiar_gender6': rec.partner_id.familiar_gender6,
                    'familiar_gender7': rec.partner_id.familiar_gender7,
                    'familiar_gender8': rec.partner_id.familiar_gender8,
                    'familiar_gender9': rec.partner_id.familiar_gender9,
                    'familiar_gender10': rec.partner_id.familiar_gender10,
                    'familiar_address1': rec.partner_id.familiar_address1,
                    'familiar_address2': rec.partner_id.familiar_address2,
                    'familiar_address3': rec.partner_id.familiar_address3,
                    'familiar_address4': rec.partner_id.familiar_address4,
                    'familiar_address5': rec.partner_id.familiar_address5,
                    'familiar_address6': rec.partner_id.familiar_address6,
                    'familiar_address7': rec.partner_id.familiar_address7,
                    'familiar_address8': rec.partner_id.familiar_address8,
                    'familiar_address9': rec.partner_id.familiar_address9,
                    'familiar_address10': rec.partner_id.familiar_address10,
                    'is_beneficiary1': rec.partner_id.is_beneficiary1,
                    'is_beneficiary2': rec.partner_id.is_beneficiary2,
                    'is_beneficiary3': rec.partner_id.is_beneficiary3,
                    'is_beneficiary4': rec.partner_id.is_beneficiary4,
                    'is_beneficiary5': rec.partner_id.is_beneficiary5,
                    'is_beneficiary6': rec.partner_id.is_beneficiary6,
                    'is_beneficiary7': rec.partner_id.is_beneficiary7,
                    'is_beneficiary8': rec.partner_id.is_beneficiary8,
                    'is_beneficiary9': rec.partner_id.is_beneficiary9,
                    'is_beneficiary10': rec.partner_id.is_beneficiary10,
                    'private_pension_system': rec.partner_id.private_pension_system,
                    'afp_first_job': rec.partner_id.afp_first_job,
                    'coming_from_onp': rec.partner_id.coming_from_onp,
                    'national_pension_system': rec.partner_id.national_pension_system,
                    'identification_type': rec.partner_id.l10n_latam_identification_type_id.name,
                    'job': rec.partner_id.employee_ids.job_id.name
                })



    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)


    def has_to_be_signed(self, include_draft=False):
        return (self.state in ('draft','to_sign') or (self.state in ('draft','to_sign') and include_draft)) and not self.applicant_signature


    def _get_portal_return_action(self):
        self.ensure_one()
        return self.env.ref('mkt_recruitment.view_recruitment_document_action')


    def _compute_access_url(self):
        super(RecruitmentDocument, self)._compute_access_url()
        for document in self:
            document.access_url = '/my/documents/%s' % (document.id)


    def preview_recruitment_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url()
        }


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.document') or _('New')
        return super(RecruitmentDocument, self).create(vals)
