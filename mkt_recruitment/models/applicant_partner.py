from odoo import _, api, fields, models
from odoo.addons.mkt_recruitment.models.apiperu import apiperu_dni
from odoo.exceptions import ValidationError


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

education_levels = [
    ('wo_formal_education', 'WITHOUT FORMAL EDUCATION'),
    ('incomplete_special_education', 'INCOMPLETE SPECIAL EDUCATION'),
    ('complete_special_education', 'COMPLETE SPECIAL EDUCATION'),
    ('incomplete_primary_education', 'INCOMPLETE PRIMARY EDUCATION'),
    ('complete_primary_education', 'COMPLETE PRIMARY EDUCATION'),

    ('incomplete_seconday_education', 'INCOMPLETE SECONDARY EDUCATION'),
    ('complete_secondary_education', 'COMPLETE SECONDARY EDUCATION'),
    ('incomplete_technical_education', 'INCOMPLETE TECHNICAL EDUCATION'),
    ('complete_technical_education', 'COMPLETE TECHNICAL EDUCATION'),

    ('incomplete_higher_education', 'INCOMPLETE HIGHER EDUCATION(HIGHER INSTITUTE, ETC)'),
    ('complete_higher_education', 'COMPLETE HIGHER EDUCATION(HIGHER INSTITUTE, ETC)'),
    ('incomplete_universitary_education', 'INCOMPLETE UNIVERSITARY EDUCATION'),
    ('complete_universitary_education', 'COMPLETE UNIVERSITARY EDUCATION'),
    ('bachelor_degree', 'BACHELOR DEGREE'),

    ('titled', 'TITLED'),
    ('incomplete_masters_studies', 'INCOMPLETE STUDIES OF MASTER'),
    ('complete_masters_studies', 'COMPLETE STUDIES OF MASTER'),
    ('master_degree', 'MASTER DEGREE'),
    ('complete_doctoral_studies', 'COMPLETE DOCTORAL STUDIES'),
    ('incomplete_doctoral_studies', 'INCOMPLETE DOCTORAL STUDIES'),
    ('doctoral_degree', 'DOCTORAL DEGREE'),
]

states = [
    ('draft', 'Draft'),
    ('not_found', 'Not found'),
    ('uploaded', 'Uploaded'),
]

def get_default_country(self):
    return self.env['res.country'].search([('code','=','PE')]).id


def get_default_identification_type_id(self):
    identification_type = self.env['l10n_latam.identification.type'].search([('name', '=', 'DNI')], limit=1)
    return identification_type.id if identification_type else False

class ApplicantPartner(models.Model):
    _name = 'applicant.partner'
    _description = 'Application partner'
    _order = 'id desc'

    name = fields.Char(string='Name')
    dni = fields.Char(string='DNI')
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    gender = fields.Selection(selection=genders, string='Gender')
    birthday = fields.Date(string='Date of birth')
    marital = fields.Selection(selection=[
        ('Soltero/a', 'Single'),
        ('Casado/a', 'Married'),
        ('Conviviente','Legal Conviviente'),
        ('Viudo/a', 'Widower'),
        ('Divorciado/a', 'Divorced'),
    ], default='Soltero/a', string='Marital status')
    children = fields.Integer(string='Children')
    emergency_contact = fields.Char(string='Emergency contact')
    emergency_phone = fields.Char(string='Emergency phone')
    age = fields.Integer(string='Age')
    nationality_id = fields.Many2one(comodel_name='res.country', default=get_default_country, string='Nationality')
    demonym = fields.Char(related='nationality_id.demonym', string='Demonym')
    identification_type_id = fields.Many2one(comodel_name='l10n_latam.identification.type', string='Identification', default=get_default_identification_type_id)
    country_id = fields.Many2one(comodel_name='res.country', default=get_default_country, string='Country')
    state_id = fields.Many2one(comodel_name='res.country.state', string='Province')
    city_id = fields.Many2one(comodel_name='res.city', string='City')
    district_id = fields.Many2one(comodel_name='l10n_pe.res.city.district', string='District')
    zip = fields.Char(string='Zip code')
    street = fields.Char(string='Street')
    reference_location = fields.Char(string='Reference location')
    
    education_level = fields.Selection(selection=education_levels, string='Level')
    education_start_date = fields.Date(string='Start Date')
    education_end_date = fields.Date(string='End Date')
    institution = fields.Char(string='Institution')
    profession = fields.Char(string='Profession')

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

    private_pension_system = fields.Boolean(default=False, string='Private pension system')
    afp_first_job = fields.Boolean(default=False, string='(AFP) First job')
    coming_from_onp = fields.Boolean(default=False, string='Coming from ONP')
    national_pension_system = fields.Boolean(default=False, string='National pension system')

    state = fields.Selection(selection=states, default='draft', string='State', tracking=True)

    def send_email(self):
        template = self.env.ref('mkt_recruitment.mail_applicant_partner_filled')
        for rec in self:
            template.send_mail(rec.id, force_send=True)


    def update_partner(self):
        for rec in self:
            partner = self.env['res.partner'].search([('vat','=',rec.dni)])
            if partner:
                if not partner.is_validate:
                    partner.sudo().write({
                        'name': rec.name,
                        'vat': rec.dni,
                        'personal_email': rec.email,
                        'gender': rec.gender,
                        'phone': rec.phone,
                        'birthday': rec.birthday,
                        'marital': rec.marital,
                        'nationality_id': rec.nationality_id.id,
                        'l10n_latam_identification_type_id': rec.identification_type_id.id,
                        'children': rec.children,
                        'emergency_contact': rec.emergency_contact,
                        'emergency_phone': rec.emergency_phone,
                        'age': rec.age,
                        'country_id': rec.country_id.id,
                        'state_id': rec.state_id.id,
                        'city_id': rec.city_id.id,
                        'l10n_pe_district': rec.district_id,
                        'zip': rec.zip,
                        'street': rec.street,
                        'reference_location': rec.reference_location,
                        'familiar_dni1': rec.familiar_dni1,
                        'familiar_dni2': rec.familiar_dni2,
                        'familiar_dni3': rec.familiar_dni3,
                        'familiar_dni4': rec.familiar_dni4,
                        'familiar_dni5': rec.familiar_dni5,
                        'familiar_dni6': rec.familiar_dni6,
                        'familiar_dni7': rec.familiar_dni7,
                        'familiar_dni8': rec.familiar_dni8,
                        'familiar_dni9': rec.familiar_dni9,
                        'familiar_dni10': rec.familiar_dni10,
                        'familiar_address1': rec.familiar_address1,
                        'familiar_address2': rec.familiar_address2,
                        'familiar_address3': rec.familiar_address3,
                        'familiar_address4': rec.familiar_address4,
                        'familiar_address5': rec.familiar_address5,
                        'familiar_address6': rec.familiar_address6,
                        'familiar_address7': rec.familiar_address7,
                        'familiar_address8': rec.familiar_address8,
                        'familiar_address9': rec.familiar_address9,
                        'familiar_address10': rec.familiar_address10,
                        'familiar_birthday1': rec.familiar_birthday1,
                        'familiar_birthday2': rec.familiar_birthday2,
                        'familiar_birthday3': rec.familiar_birthday3,
                        'familiar_birthday4': rec.familiar_birthday4,
                        'familiar_birthday5': rec.familiar_birthday5,
                        'familiar_birthday6': rec.familiar_birthday6,
                        'familiar_birthday7': rec.familiar_birthday7,
                        'familiar_birthday8': rec.familiar_birthday8,
                        'familiar_birthday9': rec.familiar_birthday9,
                        'familiar_birthday10': rec.familiar_birthday10,
                        'familiar_full_name1': rec.familiar_full_name1,
                        'familiar_full_name2': rec.familiar_full_name2,
                        'familiar_full_name3': rec.familiar_full_name3,
                        'familiar_full_name4': rec.familiar_full_name4,
                        'familiar_full_name5': rec.familiar_full_name5,
                        'familiar_full_name6': rec.familiar_full_name6,
                        'familiar_full_name7': rec.familiar_full_name7,
                        'familiar_full_name8': rec.familiar_full_name8,
                        'familiar_full_name9': rec.familiar_full_name9,
                        'familiar_full_name10': rec.familiar_full_name10,
                        'familiar_gender1': rec.familiar_gender1,
                        'familiar_gender2': rec.familiar_gender2,
                        'familiar_gender3': rec.familiar_gender3,
                        'familiar_gender4': rec.familiar_gender4,
                        'familiar_gender5': rec.familiar_gender5,
                        'familiar_gender6': rec.familiar_gender6,
                        'familiar_gender7': rec.familiar_gender7,
                        'familiar_gender8': rec.familiar_gender8,
                        'familiar_gender9': rec.familiar_gender9,
                        'familiar_gender10': rec.familiar_gender10,
                        'familiar_relationship1': rec.familiar_relationship1,
                        'familiar_relationship2': rec.familiar_relationship2,
                        'familiar_relationship3': rec.familiar_relationship3,
                        'familiar_relationship4': rec.familiar_relationship4,
                        'familiar_relationship5': rec.familiar_relationship5,
                        'familiar_relationship6': rec.familiar_relationship6,
                        'familiar_relationship7': rec.familiar_relationship7,
                        'familiar_relationship8': rec.familiar_relationship8,
                        'familiar_relationship9': rec.familiar_relationship9,
                        'familiar_relationship10': rec.familiar_relationship10,
                        'is_beneficiary1': rec.is_beneficiary1,
                        'is_beneficiary2': rec.is_beneficiary2,
                        'is_beneficiary3': rec.is_beneficiary3,
                        'is_beneficiary4': rec.is_beneficiary4,
                        'is_beneficiary5': rec.is_beneficiary5,
                        'is_beneficiary6': rec.is_beneficiary6,
                        'is_beneficiary7': rec.is_beneficiary7,
                        'is_beneficiary8': rec.is_beneficiary8,
                        'is_beneficiary9': rec.is_beneficiary9,
                        'is_beneficiary10': rec.is_beneficiary10,
                        'private_pension_system': rec.private_pension_system,
                        'afp_first_job': rec.afp_first_job,
                        'coming_from_onp': rec.coming_from_onp,
                        'national_pension_system': rec.national_pension_system,
                        'education_level': rec.education_level,
                        'education_start_date': rec.education_start_date,
                        'education_end_date': rec.education_end_date,
                        'institution': rec.institution,
                        'profession': rec.profession,
                    })
                    partner.sudo()._onchange_age()
                    self.state = 'uploaded'
                    return {
                        'effect': {
                            'fadeout': 'fast',
                            'message': _('Partner %s updated') % partner.name,
                            'type': 'rainbow_man',
                        }
                    }
                else:
                    raise ValidationError(_('''This applicant's information has already been validated and will not allow it to be changed.\nIn case you wish to update your information please inform the payroll area so that it can be devalidated and uploaded..''') )
            else:
                self.state = 'not_found'
                raise ValidationError(_(''' A contact with the same DNI has not been found in the system.\nUntil a match is found, the information cannot be uploaded.''') )


    @api.model
    def create(self, vals):
        if 'dni' in vals and isinstance(vals['dni'], str):
            vals['dni'] = vals['dni'].strip()
        try:
            vals['name'] = apiperu_dni(vals.get('dni')) or vals.get('name')
        except:
            pass
        return super(ApplicantPartner, self).create(vals)