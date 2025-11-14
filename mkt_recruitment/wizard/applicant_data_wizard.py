from odoo import models, fields, api
from odoo.exceptions import UserError

relationship = [
    ('Madre','Madre'),
    ('Padre','Padre'),
    ('Hermano','Hermano'),
    ('Hermana','Hermana'),
    ('Esposo/a','Esposo/a'),
    ('Conviviente','Conviviente'),
    ('Hijo','Hijo'),
    ('Hija','Hija'),
]

genders = [
    ('male', 'Masculino'),
    ('female', 'Femenino'),
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

class ApplicantDataWizard(models.TransientModel):
    _name = 'applicant.data.wizard'
    _description = 'Applicant Data Wizard'

    name = fields.Char(string="Nombre Completo")
    identification_type = fields.Char(string="Tipo de Identificación")
    identification_number = fields.Char(string="Número de Identificación")
    birthday = fields.Date(string="Fecha de Nacimiento")
    gender = fields.Selection(genders, string="Género")
    age = fields.Integer(string="Edad")
    # nationality_id = fields.Many2one('res.country', string="")
    demonym = fields.Char(string="Nacionalidad")
    phone = fields.Char(string="Teléfono")
    
    email = fields.Char(string="Correo Electrónico")
    personal_email = fields.Char(string="Correo Electrónico Personal")

    street = fields.Char(string="Dirección")
    reference_location = fields.Char(string="Referencia de Ubicación")
    state = fields.Char(string="Departamento")
    city = fields.Char(string="Provincia")
    district = fields.Char(string="Distrito")

    emergency_contact = fields.Char(string="Contacto de Emergencia")
    emergency_phone = fields.Char(string="Celular de Emergencia")
    emergency_contact_relationship = fields.Selection(selection=relationship, string="Parentesco de Contacto de Emergencia")

    marital = fields.Selection(selection=[
            ('Soltero/a', 'Soltero/a'),
            ('Casado/a', 'Casado/a'),
            ('Conviviente', 'Conviviente'),
            ('Viudo/a', 'Viudo/a'),
            ('Divorciado/a', 'Divorciado/a')
        ], string="Estado Civil")
    children = fields.Integer(string="N° Hijos")

    private_pension_system = fields.Boolean(string="Sistema Privado de Pensiones (AFP)")
    afp_first_job = fields.Boolean(string="Primer Empleo")
    coming_from_onp = fields.Boolean(string="Procedente de ONP")
    national_pension_system = fields.Boolean(string="Sistema Nacional de Pensiones (ONP)")
    fifth_category_income = fields.Boolean(string="Renta de Quinta Categoría de Otros Empleadores")

    education_level = fields.Selection(selection=education_levels, string="Nivel de Educación")

    current_dni = fields.Binary(string='DNI Vigente (Frontal)')
    current_dni_filename = fields.Char(string='Nombre Archivo DNI Vigente (Frontal)')
    is_current_dni = fields.Boolean(string='DNI Vigente (Frontal)?')

    current_dni_back = fields.Binary(string='DNI Vigente (Posterior)')
    current_dni_back_filename = fields.Char(string='Nombre Archivo DNI Vigente (Posterior)')
    is_current_dni_back = fields.Boolean(string='DNI Vigente (Posterior)?')

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

    child_dnifile1 = fields.Binary(string='DNI hijo 1 (Frente)')
    child_dnifile2 = fields.Binary(string='DNI hijo 2 (Frente)')
    child_dnifile3 = fields.Binary(string='DNI hijo 3 (Frente)')
    child_dnifile4 = fields.Binary(string='DNI hijo 4 (Frente)')
    child_dnifile5 = fields.Binary(string='DNI hijo 5 (Frente)')
    child_dnifile6 = fields.Binary(string='DNI hijo 6 (Frente)')

    child_dnifile1_filename = fields.Char(string='Filename DNI hijo 1 (Frente)')
    child_dnifile2_filename = fields.Char(string='Filename DNI hijo 2 (Frente)')
    child_dnifile3_filename = fields.Char(string='Filename DNI hijo 3 (Frente)')
    child_dnifile4_filename = fields.Char(string='Filename DNI hijo 4 (Frente)')
    child_dnifile5_filename = fields.Char(string='Filename DNI hijo 5 (Frente)')
    child_dnifile6_filename = fields.Char(string='Filename DNI hijo 6 (Frente)')

    child_dnifile1_back = fields.Binary(string='DNI hijo 1 (Reverso)')
    child_dnifile2_back = fields.Binary(string='DNI hijo 2 (Reverso)')
    child_dnifile3_back = fields.Binary(string='DNI hijo 3 (Reverso)')
    child_dnifile4_back = fields.Binary(string='DNI hijo 4 (Reverso)')
    child_dnifile5_back = fields.Binary(string='DNI hijo 5 (Reverso)')
    child_dnifile6_back = fields.Binary(string='DNI hijo 6 (Reverso)')

    child_dnifile1_back_filename = fields.Char(string='Filename DNI hijo 1 (Reverso)')
    child_dnifile2_back_filename = fields.Char(string='Filename DNI hijo 2 (Reverso)')
    child_dnifile3_back_filename = fields.Char(string='Filename DNI hijo 3 (Reverso)')
    child_dnifile4_back_filename = fields.Char(string='Filename DNI hijo 4 (Reverso)')
    child_dnifile5_back_filename = fields.Char(string='Filename DNI hijo 5 (Reverso)')
    child_dnifile6_back_filename = fields.Char(string='Filename DNI hijo 6 (Reverso)')

    @api.model
    def default_get(self, fields):
        res = super(ApplicantDataWizard, self).default_get(fields)
        applicant_id = self.env.context.get('active_id')
        if applicant_id:
            applicant = self.env['hr.applicant'].browse(applicant_id)
            partner = applicant.partner_id
            if partner:
                res.update({

                    'name': partner.name,
                    'identification_type': partner.l10n_latam_identification_type_id.name,
                    'identification_number': partner.vat,
                    'birthday': partner.birthday, 
                    'gender': partner.gender,
                    'age': partner.age,
                    # 'nationality_id': partner.nationality_id.id,
                    'demonym': partner.demonym,
                    'phone': partner.phone,

                    'email': partner.email,
                    'personal_email': partner.personal_email,

                    'street': partner.street,
                    'reference_location': partner.reference_location,
                    'state': partner.state_id.name,
                    'city': partner.city_id.name,
                    'district': partner.l10n_pe_district.name,

                    'emergency_contact': partner.emergency_contact,
                    'emergency_phone': partner.emergency_phone,
                    'emergency_contact_relationship': partner.emergency_contact_relationship,

                    'marital': partner.marital,
                    'children': partner.children,

                    'private_pension_system': partner.private_pension_system,
                    'afp_first_job': partner.afp_first_job,
                    'coming_from_onp': partner.coming_from_onp,
                    'national_pension_system': partner.national_pension_system,
                    'fifth_category_income': partner.fifth_category_income,

                    'education_level': partner.education_level,

                    'current_dni': partner.current_dni,
                    'current_dni_filename': partner.current_dni_filename,
                    'is_current_dni': partner.is_current_dni,
                    'current_dni_back': partner.current_dni_back,
                    'current_dni_back_filename': partner.current_dni_back_filename,
                    'is_current_dni_back': partner.is_current_dni_back,

                    'child_dni1': partner.child_dni1,
                    'child_dni2': partner.child_dni2,
                    'child_dni3': partner.child_dni3,
                    'child_dni4': partner.child_dni4,
                    'child_dni5': partner.child_dni5,
                    'child_dni6': partner.child_dni6,

                    'child_full_name1': partner.child_full_name1,
                    'child_full_name2': partner.child_full_name2,
                    'child_full_name3': partner.child_full_name3,
                    'child_full_name4': partner.child_full_name4,
                    'child_full_name5': partner.child_full_name5,
                    'child_full_name6': partner.child_full_name6,

                    'child_birthday1': partner.child_birthday1,
                    'child_birthday2': partner.child_birthday2,
                    'child_birthday3': partner.child_birthday3,
                    'child_birthday4': partner.child_birthday4,
                    'child_birthday5': partner.child_birthday5,
                    'child_birthday6': partner.child_birthday6,

                    'child_dnifile1': partner.child_dnifile1,
                    'child_dnifile2': partner.child_dnifile2,
                    'child_dnifile3': partner.child_dnifile3,
                    'child_dnifile4': partner.child_dnifile4,
                    'child_dnifile5': partner.child_dnifile5,
                    'child_dnifile6': partner.child_dnifile6,

                    'child_dnifile1_filename': partner.child_dnifile1_filename,
                    'child_dnifile2_filename': partner.child_dnifile2_filename,
                    'child_dnifile3_filename': partner.child_dnifile3_filename,
                    'child_dnifile4_filename': partner.child_dnifile4_filename,
                    'child_dnifile5_filename': partner.child_dnifile5_filename,
                    'child_dnifile6_filename': partner.child_dnifile6_filename,

                    'child_dnifile1_back': partner.child_dnifile1_back,
                    'child_dnifile2_back': partner.child_dnifile2_back,
                    'child_dnifile3_back': partner.child_dnifile3_back,
                    'child_dnifile4_back': partner.child_dnifile4_back,
                    'child_dnifile5_back': partner.child_dnifile5_back,
                    'child_dnifile6_back': partner.child_dnifile6_back,

                    'child_dnifile1_back_filename': partner.child_dnifile1_back_filename,
                    'child_dnifile2_back_filename': partner.child_dnifile2_back_filename,
                    'child_dnifile3_back_filename': partner.child_dnifile3_back_filename,
                    'child_dnifile4_back_filename': partner.child_dnifile4_back_filename,
                    'child_dnifile5_back_filename': partner.child_dnifile5_back_filename,
                    'child_dnifile6_back_filename': partner.child_dnifile6_back_filename,
                })
        return res
    

    def action_download_current_dni(self):
        self.ensure_one()
        applicant_id = self.env.context.get('active_id')
        applicant = self.env['hr.applicant'].browse(applicant_id)
        partner = applicant.partner_id

        if not partner.current_dni:
            raise UserError("No hay archivo para descargar.")

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/res.partner/{partner.id}/current_dni?download=true&filename={partner.current_dni_filename}",
            'target': 'self',
        }

    def action_download_current_dni_back(self):
        self.ensure_one()
        applicant_id = self.env.context.get('active_id')
        applicant = self.env['hr.applicant'].browse(applicant_id)
        partner = applicant.partner_id

        if not partner.current_dni_back:
            raise UserError("No hay archivo posterior para descargar.")

        return {
            'type': 'ir.actions.act_url',
            'url': f"/web/content/res.partner/{partner.id}/current_dni_back?download=true&filename={partner.current_dni_back_filename}",
            'target': 'self',
        }

