from odoo import _, api, fields, models
from datetime import timedelta, date
from babel.dates import format_date

states = [
    ('draft','Draft'),
    ('petitioner','Petitioner'),
]

currency_type = [
    ('soles', 'Soles'),
    ('dolares', 'Dólares'),
]

def get_default_country(self):
    return self.env['res.country'].search([('code','=','PE')]).id


class Affidavit(models.Model):
    _name = 'affidavit'
    _description = 'Affidavit'
    _inherit = ['portal.mixin','mail.thread','mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(required=True, default=lambda self: _('New'), string='Name', copy=False)
    amount_currency_type = fields.Selection(string='Tipo de moneda', selection=currency_type, default='soles', tracking=True)
    user_vat = fields.Char(default=lambda self: self.env.user.partner_id.vat, string='Vat')
    employee_id = fields.Many2one(comodel_name='hr.employee', default=lambda self:self.env.user.employee_id)
    job_id = fields.Many2one(comodel_name='hr.job', related='employee_id.job_id', string='Job')
    user_id = fields.Many2one(comodel_name='res.users', string='User')
    location = fields.Char(string='Location')
    country_id = fields.Many2one(comodel_name='res.country', default=get_default_country, string='Country')
    state_id = fields.Many2one(comodel_name='res.country.state', string='Department')
    city_id = fields.Many2one(comodel_name='res.city', string='Province')
    district_id = fields.Many2one(comodel_name='l10n_pe.res.city.district', string='Distrito')
    concept = fields.Char(string='Concept')
    activity = fields.Char(string='Activity')
    currency_id = fields.Many2one(comodel_name='res.currency')
    amount = fields.Monetary(currency_field='currency_id', string='Amount')
    date = fields.Date(string='Date',copy=False,tracking=True)
    state = fields.Selection(selection=states, string='State')
    from_portal = fields.Boolean(default=False, string='Creado en portal')
    date_month = fields.Char(string="Mes", compute="_compute_date_month", store=True)

    petitioner_signature = fields.Binary(string='Petitioner')
    executive_signature = fields.Binary(string='Executive')


    def preview_affidavit_document(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }


    def _compute_access_url(self):
        super(Affidavit, self)._compute_access_url()
        for affidavit in self:
            affidavit.access_url = 'my/affidavits/%s' % (affidavit.id)


    @api.onchange('amount_currency_type')
    def _onchange_currency(self):
        if self.amount_currency_type == 'soles':
            soles = self.env['res.currency'].search([('name','=','PEN')])
            self.currency_id = soles.id
        if self.amount_currency_type == 'dolares':
            dolares = self.env['res.currency'].search([('name','=','USD')])
            self.currency_id = dolares.id


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('affidavit') or _('New')
        affidavit = super(Affidavit, self).create(vals)
        return affidavit


    @api.depends('date')
    def _compute_date_month(self):
        for rec in self:
            if rec.date:
                rec.date_month = format_date(rec.date, format='MMMM', locale='es_PE').capitalize()
            else:
                rec.date_month = ''