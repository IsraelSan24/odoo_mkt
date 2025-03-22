from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta
from datetime import timedelta, date
from odoo.exceptions import UserError
from odoo.addons.mkt_recruitment.models.number_to_string import number_to_string
import base64
import logging
from geopy.geocoders import Nominatim
import user_agents
import random
import string
from babel.dates import format_date
_logger = logging.getLogger(__name__)

signature_states = [
    ('to_sign','To Sign'),
    ('cancel','Cancel'),
    ('signed','Signed'),
]

def employer_signature_default(self):
    default = self.env['employer.signature'].search([('signature_default','=',True)])
    return default.id


class Contract(models.Model):
    _name = 'hr.contract'
    _inherit = ['hr.contract','portal.mixin','mail.thread','mail.activity.mixin','utm.mixin']

    name = fields.Char(copy=False, default=lambda self: _('New'), required=True, string="Name")

    contract_signature = fields.Image(copy=False, string='Signature', attachment=True, tracking=True)
    signed_by = fields.Char(string='Signed by', copy=False,tracking=True)
    signed_on = fields.Datetime(string='Signed On', copy=False,tracking=True)
    wage_in_text = fields.Char(compute='_compute_result', string='Wage in text', tracking=True)
    contract_months = fields.Char(string='Duration of the contract', tracking=True)
    residual_contract_days = fields.Char(string='Residual contract days')
    signature_state = fields.Selection(selection=signature_states, string='Employee signature status', copy=False)
    signature_employer_state = fields.Selection(selection=signature_states, string='Signature employer state', default='to_sign', copy=False)
    is_renovation = fields.Boolean(default=False, string='Renovation', tracking=True)
    signed_by_employer = fields.Boolean(default=False, string='Signed by employer', copy=False, tracking=True)
    employer_signature_id = fields.Many2one(comodel_name='employer.signature', default=employer_signature_default, string='Employer signature', tracking=True)
    employer_signed_on = fields.Datetime(string='Signed by employer on', copy=False, tracking=True)
    is_sended = fields.Boolean(default=False, string='Send contract', tracking=True)
    email_contract_signed_send_on = fields.Datetime(string='Contract signed email sent at', copy=False)
    email_contract_cancelled_on = fields.Datetime(string='Contract cancelled email sent at', copy=False)
    hr_responsible_id = fields.Many2one(comodel_name='res.users', default=lambda self: self.env.user, string='Responsible',
                                        tracking=True, help='Person responsible for validating the employee\'s contracts.')
    is_back_office = fields.Boolean(default=False, string='Back office')
    partner_name = fields.Char(string='Name')
    vat = fields.Char(string='Vat')
    street = fields.Char(string='Street')
    district = fields.Char(string='District')
    province = fields.Char(string='Province')
    department = fields.Char(string='Department')
    employee_job = fields.Char(string='Job')
    age = fields.Char(string='Age')
    phone = fields.Char(string='Phone')
    email = fields.Char(string='Email')
    country = fields.Char(string="Country")
    nationality = fields.Char(string='Nationality')
    profession = fields.Char(string="Profession")
    education_level = fields.Char(string="Education level")
    gender = fields.Char(string="Gender")
    marital = fields.Char(string="Marital")
    company_vat = fields.Char(string='Company vat')
    cost_center = fields.Char(required=True, string='Cost center')
    employer_signature = fields.Binary(string="Signature", copy=False, attachment=True)

    date_start_month = fields.Char(compute='_compute_date_start_month', store=True)
    date_end_month = fields.Char(compute='_compute_date_end_month', store=True)

    signed_on_month = fields.Char(compute='_compute_signed_on_month', store=True)
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
        return ( enteredcode == self.validation_password ) and self.state == 'draft' and not self.contract_signature


    def send_email_to_validate_contract(self):
        self = self.sudo()
        self.validation_password = ''.join(random.choice(string.digits) for i in range(4))
        mail_obj = self.env['mail.mail'].sudo()
        subject = 'Validation code of Marketing Alterno contract'
        body = '''
            Hola, tu código de verificación para firmar tu contracto es el siguiente:\n
            %s
        ''' % ( self.validation_password )
        email_to = self.sudo().email
        mail = mail_obj.create({
            'subject': subject,
            'body_html': body,
            'email_to': email_to,
        })
        mail.send()


    def geolocation(self, latitude, longitude, ip, user_agent):
        self = self.sudo()
        self.ensure_one()
        _logger.info('\n\n\n self.env.context: %s \n\n\n', self.env.context)
        geolocator = Nominatim(user_agent='my-app')
        location = geolocator.reverse(str(latitude) + ', ' + str(longitude))
        self.latitude = latitude
        self.longitude = longitude
        self.ip = ip
        self.user_agents = user_agent
        ua = user_agents.parse(user_agent)
        device_info = f"{ua.device.family} / {ua.os.family} {ua.os.version_string} / {ua.browser.family} {ua.browser.version_string}"
        device = str(ua).split('/')[0]
        self.device_info = ua
        self.location_maps = 'https://www.google.com/maps/place/' + location.address
        self.device = device
        self.os = ua.os.family
        self.browser = ua.browser.family
        _logger.info('\n\n\n device_info: %s \n\n\n', device_info)


    def update_locale_date(self):
        for rec in self:
            rec._compute_date_start_month()
            rec._compute_date_end_month()
            rec._compute_signed_on_month()


    @api.depends('date_start')
    def _compute_date_start_month(self):
        for rec in self:
            if rec.date_start:
                rec.date_start_month = format_date(rec.date_start, format='MMMM', locale='es_PE')
            else:
                rec.date_start_month = ''


    @api.depends('date_end')
    def _compute_date_end_month(self):
        for rec in self:
            if rec.date_end:
                rec.date_end_month = format_date(rec.date_end, format='MMMM', locale='es_PE')
            else:
                rec.date_end_month = ''


    @api.depends('signed_on')
    def _compute_signed_on_month(self):
        for rec in self:
            if rec.signed_on:
                rec.signed_on_month = format_date(rec.signed_on, format='MMMM', locale='es_PE')
            else:
                rec.signed_on_month = ''


    def send_email_to_employee_signed(self):
        template = self.env.ref('mkt_recruitment.mail_contract_signed')
        for rec in self:
            template.send_mail(rec.id, force_send=True)
            rec.email_contract_signed_send_on = fields.Datetime.now()
            rec.message_post(
                body = _('The email to comunicate the contract was signed was sent  to %s ( %s ) at %s.') % (
                    rec.employee_id.name, rec.employee_id.address_home_id.personal_email, rec.email_contract_signed_send_on
                )
            )


    def send_email_to_employee_canceled(self):
        template = self.env.ref('mkt_recruitment.mail_contract_cancelled')
        for rec in self:
            template.send_mail(rec.id, force_send=True)
            rec.email_contract_cancelled_on = fields.Datetime.now()
            rec.message_post(
                body = _( 'The email to comunicate the contract was cancelled was sent to %s ( %s ) at %s.' ) % (
                    rec.employee_id.name, rec.employee_id.address_home_id.personal_email, rec.email_contract_cancelled_on
                )
            )


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('hr.contract') or _('New')
        res = super(Contract, self).create(vals)
        res.write_data()
        return res


    # def write(self,vals):
    #     if 'state' in vals:
    #         if vals['state'] != self.state:
    #             if not self.env.context.get('from_signed_function', False):
    #                 raise UserError("No puedes cambiar el estado a 'Done' mediante arrastre en Kanban.")
    #     res = super(Contract, self).write(vals)
    #     return res


    def button_refuse(self):
        self.signature_employer_state = 'cancel'
        self.signature_state = 'cancel'
        self.contract_signature = False
        self.signed_by = False
        self.signed_on = False
        self.signed_by_employer = False
        self.send_email_to_employee_canceled()
        self.with_context(from_signed_function=True).write({'state': 'cancel'})


    @api.model
    def update_state(self):
        contracts_to_close = self.search([
            ('state', '=', 'open'),
            '|',
            ('date_end', '<=', fields.Date.to_string(date.today())),
            ('visa_expire', '<=', fields.Date.to_string(date.today())),
        ])
        if contracts_to_close:
            self.with_context(from_signed_function=True).write({'state': 'close'})
        res = super(Contract, self).update_state()
        return res


    def signed(self):
        self.state = 'signed'


    @api.depends('wage')
    def _compute_result(self):
        for rec in self:
            res = number_to_string(rec.wage)
            rec.wage_in_text = res


    @api.onchange('date_start','date_end')
    def _compute_contract_duration(self):
        for record in self:
            if record.date_start and record.date_end:
                start_date = fields.Date.from_string(record.date_start)
                end_date = fields.Date.from_string(record.date_end)
                
                total_months = 0
                total_days = 0
                
                current_date = start_date
                while current_date <= end_date:
                    start_month = current_date.replace(day=1)
                    end_month = (start_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                    
                    if current_date.day == 1 and end_month <= end_date:
                        total_months += 1
                        current_date = end_month + timedelta(days=1)
                    else:
                        if current_date == start_date:
                            if end_month > end_date:
                                days_in_first_month = (end_date - current_date).days + 1
                            else:
                                days_in_first_month = (end_month - current_date).days + 1
                            total_days += days_in_first_month
                            current_date = end_month + timedelta(days=1)
                        elif current_date.month == end_date.month and current_date.year == end_date.year:
                            remaining_days = (end_date - current_date).days + 1
                            total_days += remaining_days
                            break
                        else:
                            days_in_month = (end_month - current_date).days + 1
                            total_days += days_in_month
                            current_date = end_month + timedelta(days=1)
                if total_months == 0:
                    record.contract_months = f'{total_days} días'
                if total_days == 0:
                    record.contract_months = f'{total_months} meses'
                if total_months != 0 and total_days != 0:
                    record.contract_months = f'{total_months} meses y {total_days} días'
            else:
                record.contract_months = '0 meses y 0 días'


    def _get_report_base_filename(self):
        self.ensure_one()
        return '%s' % (self.name)


    def _compute_access_url(self):
        super(Contract, self)._compute_access_url()
        for contract in self:
            contract.access_url = '/my/contracts/%s' % (contract.id)


    def has_to_be_signed(self, include_draft=False):
        return (self.state == 'draft' or (self.state == 'draft' and include_draft)) and not self.contract_signature


    def _get_portal_return_action(self):
        self.ensure_one()
        return self.env.ref('hr_contract.action_hr_contract')


    def preview_contract_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def button_signature_employer_state(self):
        for rec in self:
            if rec.state == 'cancel':
                rec.signature_employer_state = 'cancel'
                rec.signature_state = 'cancel'
            else:
                if rec.contract_signature and isinstance(rec.contract_signature, bytes):
                    rec.signature_state = 'signed'
                else:
                    rec.signature_state = 'to_sign'
                if rec.employer_signature and isinstance(rec.employer_signature, bytes):
                    rec.signature_employer_state = 'signed'
                else:
                    rec.signature_employer_state = 'to_sign'
                if rec.state in ['draft', 'open']:
                    if rec.signature_state == 'signed' and rec.signature_employer_state == 'signed':
                       rec.state = 'open'
                    elif rec.signature_employer_state != 'signed':
                        rec.state = 'draft'


    def button_employer_signature(self):
        for rec in self:
            if rec.signature_employer_state == 'to_sign':
                rec.signature_employer_state = 'signed'
                if rec.state == 'draft':
                    rec.state = 'open'
                rec.signed_by_employer = True
                rec.employer_signature = rec.employer_signature_id.signature
                pdf_content = rec.env.ref('mkt_recruitment.report_contract_action').sudo()._render_qweb_pdf([rec.id])[0]
                pdf_data = base64.b64encode(pdf_content)
                rec.employer_signed_on = fields.Datetime.now()
                attach = {
                    'name': rec.name,
                    'datas': pdf_data,
                    'store_fname': rec.name,
                    'res_model': rec._name,
                    'res_id': rec.id,
                    'type': 'binary',
                }
                rec.message_post(
                    body = _('Contract signed'),
                    attachment_ids=[rec.env['ir.attachment'].create(attach).id],
                    message_type='comment',
                )


    def get_tag_education_level(self):
        for rec in self:
            if rec.employee_id.address_home_id:
                selection_value = rec.employee_id.address_home_id.education_level
                if selection_value:
                    selection_dict = dict(self.env['res.partner']._fields['education_level'].selection)
                    rec.education_level = selection_dict.get(selection_value, "")
                else:
                    rec.education_level = ""
            else:
                rec.education_level = ""

    @api.onchange('employee_id')
    def write_data(self):
        self.get_tag_education_level()
        for rec in self:
            rec.sudo().write({
                'partner_name': rec.employee_id.address_home_id.name,
                'vat': rec.employee_id.address_home_id.vat,
                'street': rec.employee_id.address_home_id.street,
                'district': rec.employee_id.address_home_id.l10n_pe_district.name,
                'province': rec.employee_id.address_home_id.city_id.name,
                'department': rec.employee_id.address_home_id.state_id.name,
                'age': rec.employee_id.address_home_id.age,
                'phone': rec.employee_id.address_home_id.phone,
                'email': rec.employee_id.address_home_id.personal_email,
                'country': rec.employee_id.address_home_id.country_id.name,
                'nationality': rec.employee_id.address_home_id.nationality_id.demonym,
                'profession': rec.employee_id.address_home_id.profession,
                'gender': rec.employee_id.address_home_id.gender,
                'marital': rec.employee_id.address_home_id.marital,
                'employee_job': rec.employee_id.job_id.name,

                'cost_center': rec.employee_id.cost_center_id.partner_id.name,
                'is_back_office': rec.employee_id.is_back_office,

                'company_vat': rec.employee_id.address_home_id.vat,
            })