from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
import zipfile
import base64
import io

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

spreadsheets = [
    ('mkt_spreadsheet', 'MKT Spreadsheet'),
    ('sp_spreadsheet', 'SP Spreadsheet'),
    ('rh', 'RH'),
]

genders = [
    ('male', 'Male'),
    ('female', 'Female'),
]

education_levels = [
    ('wo_formal_education', 'SIN EDUCACIÓN FORMAL'),
    ('incomplete_special_education', 'EDUCACIÓN ESPECIAL INCOMPLETA'),
    ('complete_special_education', 'EDUCACIÓN ESPECIAL COMPLETA'),
    ('incomplete_primary_education', 'EDUCACIÓN PRIMARIA INCOMPLETA'),
    ('complete_primary_education', 'EDUCACIÓN PRIMARIA COMPLETA'),

    ('incomplete_seconday_education', 'EDUCACIÓN SECUNDARIA INCOMPLETA'),
    ('complete_secondary_education', 'EDUCACIÓN SECUNDARIA COMPLETA'),
    ('incomplete_technical_education', 'EDUCACIÓN TECNICA INCOMPLETA'),
    ('complete_technical_education', 'EDUCACIÓN TECNICA COMPLETA'),

    ('incomplete_higher_education', 'EDUCACIÓN SUPERIOR (INSTITUTO SUPERIOR, ETC) INCOMPLETA'),
    ('complete_higher_education', 'EDUCACIÓN SUPERIOR (INSTITUTO SUPERIOR, ETC) COMPLETA'),
    ('incomplete_universitary_education', 'EDUCACIÓN UNIVERSITARIA INCOMPLETA'),
    ('complete_universitary_education', 'EDUCACIÓN UNIVERSITARIA COMPLETA'),
    ('bachelor_degree', 'GRADO DE BACHILLER'),

    ('titled', 'TITULADO'),
    ('incomplete_masters_studies', 'ESTUDIOS DE MAESTRÍA INCOMPLETA'),
    ('complete_masters_studies', 'ESTUDIOS DE MAESTRÍA COMPLETA'),
    ('master_degree', 'GRADO DE MAESTRÍA'),
    ('complete_doctoral_studies', 'ESTUDIOS DE DOCTORADO COMPLETO'),
    ('incomplete_doctoral_studies', 'ESTUDIOS DE DOCTORADO INCOMPLETO'),
    ('doctoral_degree', 'GRADO DE DOCTOR'),
]

def get_default_country(self):
    return self.env['res.country'].search([('code','=','PE')]).id


class Partner(models.Model):
    _inherit = 'res.partner'

    personal_email = fields.Char(string='Personal email')
    reference_location = fields.Char(string='Reference location')
    gender = fields.Selection(selection=genders, string='Gender')
    birthday = fields.Date(string='Date of Birth')
    emergency_contact = fields.Char(string='Emergency contact')
    emergency_phone = fields.Char(string='Emergency phone')
    emergency_contact_relationship = fields.Selection(selection=relationship)
    marital = fields.Selection(selection=[
        ('Soltero/a', 'Single'),
        ('Casado/a', 'Married'),
        ('Conviviente', 'Legal Conviviente'),
        ('Viudo/a', 'Widower'),
        ('Divorciado/a', 'Divorced')
    ], default='Soltero/a', string='Marital Status')
    age = fields.Integer(string='Age')
    children = fields.Integer(string='Children')
    family_ids = fields.One2many('res.partner.family', 'partner_id', string='Family')
    country_id = fields.Many2one(comodel_name='res.country', default=get_default_country, string='Country', ondelete='restrict')
    private_pension_system = fields.Boolean(default=False, string='Private pension system')
    afp_first_job = fields.Boolean(default=False, string='(AFP) First job')
    coming_from_onp = fields.Boolean(deafault=False, string='Coming from ONP')
    coming_from_afp = fields.Boolean(default=False, string='Coming from AFP')
    national_pension_system = fields.Boolean(default=False, string='National pension system')

    education_level = fields.Selection(selection=education_levels, string='Education level')
    education_start_date = fields.Date(string='Start date')
    education_end_date = fields.Date(string='End date')
    institution = fields.Char(string='Institution')
    profession = fields.Char(string='Profession')

    nationality_id = fields.Many2one(comodel_name='res.country', default=get_default_country, string='Nationality')
    demonym = fields.Char(related='nationality_id.demonym', string='Demonym')
    spreadsheet = fields.Selection(selection=spreadsheets, string='spreadsheet')


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
    
    familiar_dnifile1 = fields.Binary()
    familiar_dnifile2 = fields.Binary()
    familiar_dnifile3 = fields.Binary()
    familiar_dnifile4 = fields.Binary()
    familiar_dnifile5 = fields.Binary()
    familiar_dnifile6 = fields.Binary()
    familiar_dnifile7 = fields.Binary()
    familiar_dnifile8 = fields.Binary()
    familiar_dnifile9 = fields.Binary()
    familiar_dnifile10 = fields.Binary()

    familiar_dnifile1_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile2_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile3_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile4_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile5_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile6_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile7_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile8_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile9_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile10_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)

    familiar_dnifile1_back = fields.Binary()
    familiar_dnifile2_back = fields.Binary()
    familiar_dnifile3_back = fields.Binary()
    familiar_dnifile4_back = fields.Binary()
    familiar_dnifile5_back = fields.Binary()
    familiar_dnifile6_back = fields.Binary()
    familiar_dnifile7_back = fields.Binary()
    familiar_dnifile8_back = fields.Binary()
    familiar_dnifile9_back = fields.Binary()
    familiar_dnifile10_back = fields.Binary()

    familiar_dnifile1_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile2_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile3_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile4_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile5_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile6_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile7_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile8_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile9_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    familiar_dnifile10_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)

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

    current_dni = fields.Binary(string='Current DNI(Front)')
    current_dni_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Front)', store=True)
    is_current_dni = fields.Boolean(default=False, string='Current DNI(Front)?')

    current_dni_back = fields.Binary(string='Current DNI(Back)')
    current_dni_back_filename = fields.Char(compute='compute_document_filename', string='Current DNI filename(Back)', store=True)
    is_current_dni_back = fields.Boolean(default=False, string='Current DNI(Back)?')

    services_receipt = fields.Binary(string='Services receipt')
    services_receipt_filename = fields.Char(compute='compute_document_filename', string='Services receipt filename', store=True)
    is_services_receipt = fields.Boolean(default=False, string='Services receipt?')

    certijoven = fields.Binary(string='Certijoven')
    certijoven_filename = fields.Char(compute='compute_document_filename', string='Certijoven filename', store=True)
    is_certijoven = fields.Boolean(default=False, string='Certijoven?')

    t_record = fields.Binary(string='T-Record')
    t_record_filename = fields.Char(compute='compute_document_filename',string='T-Record filename', store=True)
    is_t_record = fields.Boolean(default=False, string='T-Record?')
    
    electronic_fine = fields.Binary(string='Electronic Fine')
    electronic_fine_filename = fields.Char(compute='compute_document_filename',string='Electronic Fine filename', store=True)
    is_electronic_fine = fields.Boolean(default=False, string='Electronic Fine?')

    certificate_of_vaccination = fields.Binary(string='Certificate of Vaccination')
    certificate_of_vaccination_filename = fields.Char(compute='compute_document_filename',string='Certificate of Vaccination filename', store=True)
    is_certificate_of_vaccination = fields.Boolean(default=False, string='Certificate of Vaccination?')

    health_card = fields.Binary(string='Health Card')
    health_card_filename = fields.Char(compute='compute_document_filename',string='Health Card filename', store=True)
    is_health_card = fields.Boolean(default=False, string='Health Card?')

    contributions_report = fields.Binary(string='Contributions Report')
    contributions_report_filename = fields.Char(compute='compute_document_filename',string='Contributions Report filename', store=True)
    is_contributions_report = fields.Boolean(default=False, string='Contributions Report?')
    
    document_okay = fields.Boolean(string='Documents okay', tracking=True)
    children_okay = fields.Boolean(string='Children okay', tracking=True)
    belong_applicant_id = fields.Many2one(comodel_name='hr.applicant', string='Belong applicant')

    is_validate = fields.Boolean(default=False, string='Is Validate')

    # Campos para hijos
    child_dni1 = fields.Char(string='DNI del hijo 1')
    child_dni2 = fields.Char(string='DNI del hijo 2')
    child_dni3 = fields.Char(string='DNI del hijo 3')
    child_dni4 = fields.Char(string='DNI del hijo 4')
    child_dni5 = fields.Char(string='DNI del hijo 5')
    child_dni6 = fields.Char(string='DNI del hijo 6')

    child_full_name1 = fields.Char(string='Nombre completo del hijo 1')
    child_full_name2 = fields.Char(string='Nombre completo del hijo 2')
    child_full_name3 = fields.Char(string='Nombre completo del hijo 3')
    child_full_name4 = fields.Char(string='Nombre completo del hijo 4')
    child_full_name5 = fields.Char(string='Nombre completo del hijo 5')
    child_full_name6 = fields.Char(string='Nombre completo del hijo 6')

    child_birthday1 = fields.Date(string='Fecha de nacimiento del hijo 1')
    child_birthday2 = fields.Date(string='Fecha de nacimiento del hijo 2')
    child_birthday3 = fields.Date(string='Fecha de nacimiento del hijo 3')
    child_birthday4 = fields.Date(string='Fecha de nacimiento del hijo 4')
    child_birthday5 = fields.Date(string='Fecha de nacimiento del hijo 5')
    child_birthday6 = fields.Date(string='Fecha de nacimiento del hijo 6')

    child_gender1 = fields.Selection(selection=genders, string='Género del hijo 1')
    child_gender2 = fields.Selection(selection=genders, string='Género del hijo 2')
    child_gender3 = fields.Selection(selection=genders, string='Género del hijo 3')
    child_gender4 = fields.Selection(selection=genders, string='Género del hijo 4')
    child_gender5 = fields.Selection(selection=genders, string='Género del hijo 5')
    child_gender6 = fields.Selection(selection=genders, string='Género del hijo 6')

    child_relationship1 = fields.Selection(selection=relationship, string='Relación del hijo 1')
    child_relationship2 = fields.Selection(selection=relationship, string='Relación del hijo 2')
    child_relationship3 = fields.Selection(selection=relationship, string='Relación del hijo 3')
    child_relationship4 = fields.Selection(selection=relationship, string='Relación del hijo 4')
    child_relationship5 = fields.Selection(selection=relationship, string='Relación del hijo 5')
    child_relationship6 = fields.Selection(selection=relationship, string='Relación del hijo 6')

    child_address1 = fields.Char(string='Dirección del hijo 1')
    child_address2 = fields.Char(string='Dirección del hijo 2')
    child_address3 = fields.Char(string='Dirección del hijo 3')
    child_address4 = fields.Char(string='Dirección del hijo 4')
    child_address5 = fields.Char(string='Dirección del hijo 5')
    child_address6 = fields.Char(string='Dirección del hijo 6')

    child_dnifile1 = fields.Binary(string='DNI hijo 1 (Frente)')
    child_dnifile2 = fields.Binary(string='DNI hijo 2 (Frente)')
    child_dnifile3 = fields.Binary(string='DNI hijo 3 (Frente)')
    child_dnifile4 = fields.Binary(string='DNI hijo 4 (Frente)')
    child_dnifile5 = fields.Binary(string='DNI hijo 5 (Frente)')
    child_dnifile6 = fields.Binary(string='DNI hijo 6 (Frente)')

    child_dnifile1_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 1 (Frente)', store=True)
    child_dnifile2_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 2 (Frente)', store=True)
    child_dnifile3_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 3 (Frente)', store=True)
    child_dnifile4_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 4 (Frente)', store=True)
    child_dnifile5_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 5 (Frente)', store=True)
    child_dnifile6_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 6 (Frente)', store=True)

    child_dnifile1_back = fields.Binary(string='DNI hijo 1 (Reverso)')
    child_dnifile2_back = fields.Binary(string='DNI hijo 2 (Reverso)')
    child_dnifile3_back = fields.Binary(string='DNI hijo 3 (Reverso)')
    child_dnifile4_back = fields.Binary(string='DNI hijo 4 (Reverso)')
    child_dnifile5_back = fields.Binary(string='DNI hijo 5 (Reverso)')
    child_dnifile6_back = fields.Binary(string='DNI hijo 6 (Reverso)')

    child_dnifile1_back_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 1 (Reverso)', store=True)
    child_dnifile2_back_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 2 (Reverso)', store=True)
    child_dnifile3_back_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 3 (Reverso)', store=True)
    child_dnifile4_back_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 4 (Reverso)', store=True)
    child_dnifile5_back_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 5 (Reverso)', store=True)
    child_dnifile6_back_filename = fields.Char(compute='compute_child_document_filename', string='Filename DNI hijo 6 (Reverso)', store=True)

    children_to_display = fields.Integer(compute='_compute_children_to_display', store=False)

    @api.depends('children')
    def _compute_children_to_display(self):
        for record in self:
            # Limitar a un máximo de 6 hijos
            if record.children and record.children > 0:
                record.children_to_display = min(record.children, 6)
            else:
                record.children_to_display = 0

    @api.depends('child_dni1', 'child_dni2', 'child_dni3', 'child_dni4', 'child_dni5', 'child_dni6',
                'child_dnifile1', 'child_dnifile2', 'child_dnifile3', 'child_dnifile4', 'child_dnifile5', 'child_dnifile6',
                'child_dnifile1_back', 'child_dnifile2_back', 'child_dnifile3_back', 'child_dnifile4_back', 'child_dnifile5_back', 'child_dnifile6_back')
    def compute_child_document_filename(self):
        for rec in self:
            # Generar nombres de archivo para los DNI de los hijos (frente)
            if rec.child_dni1 and rec.child_dnifile1:
                rec.child_dnifile1_filename = _('DNI(Frente)-Hijo-') + rec.child_dni1
            if rec.child_dni2 and rec.child_dnifile2:
                rec.child_dnifile2_filename = _('DNI(Frente)-Hijo-') + rec.child_dni2
            if rec.child_dni3 and rec.child_dnifile3:
                rec.child_dnifile3_filename = _('DNI(Frente)-Hijo-') + rec.child_dni3
            if rec.child_dni4 and rec.child_dnifile4:
                rec.child_dnifile4_filename = _('DNI(Frente)-Hijo-') + rec.child_dni4
            if rec.child_dni5 and rec.child_dnifile5:
                rec.child_dnifile5_filename = _('DNI(Frente)-Hijo-') + rec.child_dni5
            if rec.child_dni6 and rec.child_dnifile6:
                rec.child_dnifile6_filename = _('DNI(Frente)-Hijo-') + rec.child_dni6
                
            # Generar nombres de archivo para los DNI de los hijos (reverso)
            if rec.child_dni1 and rec.child_dnifile1_back:
                rec.child_dnifile1_back_filename = _('DNI(Reverso)-Hijo-') + rec.child_dni1
            if rec.child_dni2 and rec.child_dnifile2_back:
                rec.child_dnifile2_back_filename = _('DNI(Reverso)-Hijo-') + rec.child_dni2
            if rec.child_dni3 and rec.child_dnifile3_back:
                rec.child_dnifile3_back_filename = _('DNI(Reverso)-Hijo-') + rec.child_dni3
            if rec.child_dni4 and rec.child_dnifile4_back:
                rec.child_dnifile4_back_filename = _('DNI(Reverso)-Hijo-') + rec.child_dni4
            if rec.child_dni5 and rec.child_dnifile5_back:
                rec.child_dnifile5_back_filename = _('DNI(Reverso)-Hijo-') + rec.child_dni5
            if rec.child_dni6 and rec.child_dnifile6_back:
                rec.child_dnifile6_back_filename = _('DNI(Reverso)-Hijo-') + rec.child_dni6

    @api.onchange('children')
    def _onchange_children(self):
        if self.children and self.children > 0:
            count = min(self.children, 6)
            for i in range(1, count + 1):
                gender_field = f'child_gender{i}'
                relationship_field = f'child_relationship{i}'

                # Limpiar el valor por defecto primero
                if hasattr(self, relationship_field):
                    setattr(self, relationship_field, False)

                # Asignar valor solo si el género está definido
                if hasattr(self, gender_field):
                    gender = getattr(self, gender_field)
                    if gender == 'female':
                        setattr(self, relationship_field, 'Hija')
                    elif gender == 'male':
                        setattr(self, relationship_field, 'Hijo')

    @api.onchange('child_gender1', 'child_gender2', 'child_gender3', 
                'child_gender4', 'child_gender5', 'child_gender6')
    def _onchange_children_gender(self):
        # Actualizar la relación basado en el género
        for i in range(1, 7):
            gender_field = f'child_gender{i}'
            relationship_field = f'child_relationship{i}'
            
            if hasattr(self, gender_field) and getattr(self, gender_field):
                if getattr(self, gender_field) == 'female':
                    setattr(self, relationship_field, 'Hija')
                else:
                    setattr(self, relationship_field, 'Hijo')

    @api.onchange('current_dni_back')
    def onchange_current_dni_back(self):
        if self.current_dni_back:
            self.is_current_dni_back = True
        else:
            self.is_current_dni_back = False


    @api.onchange('current_dni')
    def onchange_current_dni(self):
        if self.current_dni:
            self.is_current_dni = True
        else:
            self.is_current_dni = False


    @api.onchange('services_receipt')
    def onchange_services_receipt(self):
        if self.services_receipt:
            self.is_services_receipt = True
        else:
            self.is_services_receipt = False


    @api.onchange('certijoven')
    def onchange_certijoven(self):
        if self.certijoven:
            self.is_certijoven = True
        else:
            self.is_certijoven = False


    @api.onchange('electronic_fine')
    def onchange_electronic_fine(self):
        if self.electronic_fine:
            self.is_electronic_fine = True
        else:
            self.is_electronic_fine = False


    @api.onchange('certificate_of_vaccination')
    def onchange_certificate_of_vaccination(self):
        if self.certificate_of_vaccination:
            self.is_certificate_of_vaccination = True
        else:
            self.is_certificate_of_vaccination = False


    @api.onchange('health_card')
    def onchange_health_card(self):
        if self.health_card:
            self.is_health_card = True
        else:
            self.is_health_card = False


    @api.onchange('contributions_report')
    def onchange_contributions_report(self):
        if self.contributions_report:
            self.is_contributions_report = True
        else:
            self.is_contributions_report = False


    @api.onchange('t_record')
    def onchange_t_record(self):
        if self.t_record:
            self.is_t_record = True
        else:
            self.is_t_record = False


    @api.depends('vat','current_dni','current_dni_back','services_receipt','certijoven','t_record','electronic_fine','certificate_of_vaccination','health_card','contributions_report',
                 'familiar_dnifile1','familiar_dnifile2','familiar_dnifile3','familiar_dnifile4','familiar_dnifile5','familiar_dnifile6','familiar_dnifile7','familiar_dnifile8','familiar_dnifile9','familiar_dnifile10', 
                 'familiar_dnifile1_back','familiar_dnifile2_back','familiar_dnifile3_back','familiar_dnifile4_back','familiar_dnifile5_back','familiar_dnifile6_back','familiar_dnifile7_back','familiar_dnifile8_back','familiar_dnifile9_back','familiar_dnifile10_back')
    def compute_document_filename(self):
        for rec in self:
            if rec.vat and rec.current_dni:
                rec.current_dni_filename = 'DNI-' + rec.vat
            if rec.vat and rec.current_dni_back:
                rec.current_dni_back_filename = 'DNI(posterior)-' + rec.vat
            if rec.vat and rec.services_receipt:
                rec.services_receipt_filename = rec.vat + _('-services_receipt')
            if rec.vat and rec.certijoven:
                rec.certijoven_filename = rec.vat + '-Certijoven'
            if rec.vat and rec.t_record:
                rec.t_record_filename = rec.vat + _('-T-Record')
            if rec.vat and rec.electronic_fine:
                rec.electronic_fine_filename = rec.vat +_('electronic_fine')
            if rec.vat and rec.certificate_of_vaccination:
                rec.certificate_of_vaccination_filename = rec.vat +_('certificate_of_vaccination')
            if rec.vat and rec.health_card:
                rec.health_card_filename = rec.vat +_('health_card')
            if rec.vat and rec.contributions_report:
                rec.contributions_report_filename = rec.vat +_('contributions_report')

            if rec.familiar_dni1 and rec.familiar_dnifile1:
                rec.familiar_dnifile1_filename = _('DNI(Front)-') + rec.familiar_dni1
            if rec.familiar_dni1 and rec.familiar_dnifile1_back:
                rec.familiar_dnifile1_back_filename = _('DNI(Back)-') + rec.familiar_dni1
                
            if rec.familiar_dni2 and rec.familiar_dnifile2:
                rec.familiar_dnifile2_filename = _('DNI(Front)-') + rec.familiar_dni2
            if rec.familiar_dni2 and rec.familiar_dnifile2_back:
                rec.familiar_dnifile2_back_filename = _('DNI(Back)-') + rec.familiar_dni2
                
            if rec.familiar_dni3 and rec.familiar_dnifile3:
                rec.familiar_dnifile3_filename = _('DNI(Front)-') + rec.familiar_dni3
            if rec.familiar_dni3 and rec.familiar_dnifile3_back:
                rec.familiar_dnifile3_back_filename = _('DNI(Back)-') + rec.familiar_dni3
                
            if rec.familiar_dni4 and rec.familiar_dnifile4:
                rec.familiar_dnifile4_filename = _('DNI(Front)-') + rec.familiar_dni4
            if rec.familiar_dni4 and rec.familiar_dnifile4_back:
                rec.familiar_dnifile4_back_filename = _('DNI(Back)-') + rec.familiar_dni4
                
            if rec.familiar_dni5 and rec.familiar_dnifile5:
                rec.familiar_dnifile5_filename = _('DNI(Front)-') + rec.familiar_dni5
            if rec.familiar_dni5 and rec.familiar_dnifile5_back:
                rec.familiar_dnifile5_back_filename = _('DNI(Back)-') + rec.familiar_dni5
                
            if rec.familiar_dni6 and rec.familiar_dnifile6:
                rec.familiar_dnifile6_filename = _('DNI(Front)-') + rec.familiar_dni6
            if rec.familiar_dni6 and rec.familiar_dnifile6_back:
                rec.familiar_dnifile6_back_filename = _('DNI(Back)-') + rec.familiar_dni6
                
            if rec.familiar_dni7 and rec.familiar_dnifile7:
                rec.familiar_dnifile7_filename = _('DNI(Front)-') + rec.familiar_dni7
            if rec.familiar_dni7 and rec.familiar_dnifile7_back:
                rec.familiar_dnifile7_back_filename = _('DNI(Back)-') + rec.familiar_dni7
                
            if rec.familiar_dni8 and rec.familiar_dnifile8:
                rec.familiar_dnifile8_filename = _('DNI(Front)-') + rec.familiar_dni8
            if rec.familiar_dni8 and rec.familiar_dnifile8_back:
                rec.familiar_dnifile8_back_filename = _('DNI(Back)-') + rec.familiar_dni8

            if rec.familiar_dni9 and rec.familiar_dnifile9:
                rec.familiar_dnifile9_filename = _('DNI(Front)-') + rec.familiar_dni9
            if rec.familiar_dni9 and rec.familiar_dnifile9_back:
                rec.familiar_dnifile9_back_filename = _('DNI(Back)-') + rec.familiar_dni9

            if rec.familiar_dni10 and rec.familiar_dnifile10:
                rec.familiar_dnifile10_filename = _('DNI(Front)-') + rec.familiar_dni10
            if rec.familiar_dni10 and rec.familiar_dnifile10_back:
                rec.familiar_dnifile10_back_filename = _('DNI(Back)-') + rec.familiar_dni10


    @api.onchange('birthday')
    def _onchange_age(self):
        today = fields.Date.today()
        age = relativedelta(today, self.birthday).years
        self.age = age


    def buton_update_applicant_partner(self):
        for rec in self:
            existing_applicant_partner = self.env['applicant.partner'].search([('dni', '=', rec.vat)], limit=1)
            if existing_applicant_partner:
                existing_applicant_partner.update_partner()
                self.is_validate = True
            else:
                raise UserError(_('This person did not fill out his or her Data Sheet.'))


    def button_send_documents(self):
        for rec in self:
            existing_document = self.env['recruitment.document'].search([('partner_id', '=', rec.id)], limit=1)
            if existing_document:
                if existing_document.state == 'signed':
                    raise UserError(_('This person has already signed its documents (%s).') % existing_document.name)
                else:
                    return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': _('Document %s has already been sent.\n(Archive it to send another)') % existing_document.name,
                            'type': 'custom_notification_animation',
                            'level': 'info',
                        }
                    }     
            else:
                user_id = self.env['res.users'].search([('partner_id', '=', rec.id)], limit=1)
                document = self.env['recruitment.document'].create({
                    'partner_id': rec.id,
                    'user_id': rec.belong_applicant_id.hr_responsible_contract_id.id,
                    'partner_name': rec.name,
                    'email': rec.personal_email,
                    'vat': rec.vat,
                    'street': rec.street,
                    'district': rec.l10n_pe_district.name,
                    'province': rec.city_id.name,
                    'department': rec.state_id.name,
                    'emergency_contact': rec.emergency_contact,
                    'emergency_phone': rec.emergency_phone,
                    'emergency_contact_relationship': rec.emergency_contact_relationship,
                    'birthday': rec.birthday,
                    'phone': rec.phone,
                    'company': user_id.company_id.name,
                    'company_department': user_id.company_id.state_id.name,
                    'company_vat': user_id.company_id.vat,
                    'gender': rec.gender,
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
                    'coming_from_afp': rec.coming_from_afp,
                    'national_pension_system': rec.national_pension_system,
                    'identification_type': rec.l10n_latam_identification_type_id.name,
                    'job': rec.employee_ids.job_id.name
                })
                document.send_to_sign()
                return {
                        'effect': {
                            'fadeout': 'slow',
                            'message': _('Document %s sent') % document.name,
                            'type': 'rainbow_man',
                        }
                    }               


    def attach_applicant_files(self):
        attachments_to_unlink = self.env['ir.attachment'].search([
            ('res_model', '=', self._name),
            ('res_id', '=', self.id),
            ('name', 'in', [
                getattr(self, f'{doc}_filename') for doc in [
                    'current_dni', 'current_dni_back', 'services_receipt', 
                    'certijoven', 'electronic_fine', 'certificate_of_vaccination', 
                    'health_card', 'contributions_report'
                ]
            ] + [
                getattr(self, f'child_dnifile{i}_filename') for i in range(1, 7)
                if getattr(self, f'child_relationship{i}') == 'Hijo' or 'Hija'
            ] + [
                getattr(self, f'child_dnifile{i}_back_filename') for i in range(1, 7)
                if getattr(self, f'child_relationship{i}') == 'Hijo' or 'Hija'
            ])
        ])
        attachments_to_unlink.unlink()
        attachments = []
        documents = [
            'current_dni','current_dni_back','services_receipt','certijoven',
            'electronic_fine','certificate_of_vaccination','health_card','contributions_report'
        ]
        for document in documents:
            if getattr(self, document):
                attach = {
                    'name': getattr(self, f'{document}_filename'),
                    'datas': getattr(self, f'{document}'),
                    'store_fname': getattr(self, f'{document}_filename'),
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary',
                }
                attachment = self.env['ir.attachment'].create(attach)
                attachments.append(attachment.id)
        for index in range(1, 7):
            relationship_field = f'child_relationship{index}'
            child_dni = f'child_dni{index}'
            child_dnifile = f'child_dnifile{index}'
            child_dnifile_back = f'child_dnifile{index}_back'

            if getattr(self, relationship_field) in ('Hijo','Hija') and getattr(self, child_dni) and getattr(self, child_dnifile):
                field = child_dnifile
                attach = {
                    'name': getattr(self, f'{field}_filename'),
                    'datas': getattr(self, field),
                    'store_fname': getattr(self, f'{field}_filename'),
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary',
                }
                attachment = self.env['ir.attachment'].create(attach)
                attachments.append(attachment.id)
            if getattr(self, relationship_field) in ('Hijo','Hija') and getattr(self, child_dni) and getattr(self, child_dnifile_back):
                field = child_dnifile_back
                attach = {
                    'name': getattr(self, f'{field}_filename'),
                    'datas': getattr(self, field),
                    'store_fname': getattr(self, f'{field}_filename'),
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary',
                }
                attachment = self.env['ir.attachment'].create(attach)
                attachments.append(attachment.id)

    def download_attach_files(self):
        for rec in self:
            try:
                document = self.env['recruitment.document'].search([('partner_id', '=', rec.id)],  order='create_date desc', limit=1)
                report_pdf_data_tuple_requirement = rec.env.ref('mkt_recruitment.report_recruitmentdocument_action').sudo()._render_qweb_pdf(document.id)
                report_pdf_data_requirement = report_pdf_data_tuple_requirement[0]
                report_pdf_data_tuple_life = rec.env.ref('mkt_recruitment.report_lifelaw_action').sudo()._render_qweb_pdf(document.id)
                report_pdf_data_life = report_pdf_data_tuple_life[0]
            except Exception as e:
                raise ValidationError(_('Error al generar los reportes: %s') % str(e))
            allowed_mimetypes = [
                'application/pdf',
                'image/jpeg',
                'image/png',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/msword',
            ]
            attachments = self.env['ir.attachment'].search([
                ('res_model', '=', rec._name),
                ('res_id', '=', rec.id),
                ('mimetype', 'in', allowed_mimetypes),
            ])

            if not attachments and not (report_pdf_data_requirement or report_pdf_data_life):
                raise ValidationError(_('No se encontraron archivos permitidos ni reportes para descargar.'))

            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for attachment in attachments:
                    if not attachment.datas:
                        continue

                    file_name = attachment.name or 'file'
                    extension_map = {
                        'application/pdf': '.pdf',
                        'image/jpeg': '.jpg',
                        'image/png': '.png',
                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
                        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
                        'application/msword': '.doc',
                    }
                    file_extension = extension_map.get(attachment.mimetype, '')
                    if not file_name.lower().endswith(file_extension):
                        file_name += file_extension

                    file_data = base64.b64decode(attachment.datas)
                    zip_file.writestr(file_name, file_data)

                zip_file.writestr('Recruitment_Document.pdf', report_pdf_data_requirement)

                zip_file.writestr('Life_Law_Report.pdf', report_pdf_data_life)

            zip_buffer.seek(0)

            zip_attachment = self.env['ir.attachment'].create({
                'name': f'{rec.name}.zip',
                'datas': base64.b64encode(zip_buffer.getvalue()),
                'type': 'binary',
                'mimetype': 'application/zip',
            })

            return {
                'type': 'ir.actions.act_url',
                'url': '/web/content/%s?download=true' % zip_attachment.id,
                'target': 'self',
            }