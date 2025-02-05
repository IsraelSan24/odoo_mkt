from odoo import _, api, fields, models
from dateutil.relativedelta import relativedelta

class ResPartnerFamily(models.Model):
    _name = 'res.partner.family'
    _description = 'Partner family'
    _order = 'id asc'

    name = fields.Char(string='Name')
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')
    gender = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
    ], string='Gender')
    birthday = fields.Date(string='Date of Birth')
    age = fields.Integer(compute='_compute_age', string='Age')
    ocupation = fields.Char(string='Ocupation')
    relationship = fields.Selection(selection=[
        ('Madre','Mother'),
        ('Padre','Father'),
        ('Hermano','Brother'),
        ('Hermana','Sister'),
        ('Esposo/a','Spouse'),
        ('Conviviente','Concubine'),
        ('Hijo','Son'),
        ('Hija','Daughter'),
    ])
    dni = fields.Char(string='DNI')
    dni_file = fields.Binary(string='DNI File')
    dni_filename = fields.Char(compute='compute_document_filename', string='Filename')
    dni_file_back = fields.Binary(string='DNI File Back')
    dni_filename_back = fields.Char(compute='compute_document_filename_back', string='Filename back')
    address = fields.Char(string='Address')


    @api.depends('birthday')
    def _compute_age(self):
        for rec in self:
            today = fields.Date.today()
            age = relativedelta(today, rec.birthday).years
            rec.age = age


    @api.depends('dni_file')
    def compute_document_filename(self):
        for rec in self:
            if rec.dni_file:
                rec.dni_filename = 'DNI-' + ( rec.dni )
            else:
                rec.dni_filename = False


    @api.depends('dni_file_back')
    def compute_document_filename_back(self):
        for rec in self:
            if rec.dni_file_back:
                rec.dni_filename_back = 'DNI(posterior)-' + ( rec.dni )
            else:
                rec.dni_filename_back = False
