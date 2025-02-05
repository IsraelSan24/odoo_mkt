from odoo import fields, models, tools

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

class SummaryEmployees(models.Model):
    _name = 'summary.employees'
    _description = 'Sumary Employees'
    _auto = False

    name = fields.Char(string='Name')
    job_id = fields.Many2one(comodel_name='hr.job', string='Job')
    department_id = fields.Many2one(comodel_name='hr.department', string='Department')
    phone = fields.Char(string='Phone')
    birthday = fields.Char(string='Birthday')
    age = fields.Integer(string='Age')
    l10n_pe_district = fields.Many2one(comodel_name='l10n_pe.res.city.district', string='District')
    education_level = fields.Selection(selection=education_levels, string='Education level')
    profession = fields.Char(string='Profession')
    children = fields.Integer(string='Children')
    user_id = fields.Many2one(comodel_name='res.users', string='Responsible')
    first_contract_date = fields.Char(string='First contract date')
    date_end = fields.Char(string='Date end')
    state = fields.Char(string='State')
    employee_create_date = fields.Datetime(string='Create date')

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(""" CREATE or REPLACE view %s AS (
                %s
                FROM %s AS rp
                %s
                )""" %(self._table, self._select(), self._from(), self._join()))


    def _select(self):
        select = """
            SELECT
                rp.id as id,
                he.create_date as employee_create_date,
                rp.name as name,
                ha.job_id as job_id,
                he.department_id as department_id,
                rp.phone as phone,
                rp.birthday as birthday,
                rp.age as age,
                rp.l10n_pe_district as l10n_pe_district,
                rp.education_level as education_level,
                rp.profession as profession,
                rp.children as children,
                rd.user_id as user_id,
                hc.state as state,
                he.first_contract_date as first_contract_date,
                hch.date_end as date_end
        """
        return select


    def _from(self):
        return 'res_partner'


    def _join(self):
        join = """
                LEFT JOIN hr_applicant as ha ON rp.belong_applicant_id = ha.id
                LEFT JOIN hr_employee as he ON ha.emp_id = he.id
                LEFT JOIN recruitment_document as rd ON rp.id = rd.partner_id
                LEFT JOIN hr_contract_history as hch ON he.id = hch.id
                LEFT JOIN hr_contract as hc ON hch.contract_id = hc.id
            WHERE rp.belong_applicant_id IS NOT NULL AND ha.emp_id IS NOT NULL AND he.active IS TRUE
        """
        return join