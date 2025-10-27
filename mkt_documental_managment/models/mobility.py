# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.tools import ustr
from odoo.exceptions import ValidationError, UserError
from datetime import datetime
from odoo.addons.mkt_documental_managment.models.signature import signature_generator

state = [
    ('draft', 'Draft'),
    ('executive', 'Executive'),
    ('done', 'Done'),
    ('refused', 'Refused'),
]

def get_default_dni(self):
    return self.env.user.vat

months = [('enero', 'Enero'), ('febrero', 'Febrero'), ('marzo', 'Marzo'),
          ('abril', 'Abril'), ('mayo', 'Mayo'), ('junio', 'Junio'),
          ('julio', 'Julio'), ('agosto', 'Agosto'), ('septiembre', 'Septiembre'),
          ('octubre', 'Octubre'), ('noviembre', 'Noviembre'), ('diciembre', 'Diciembre')]

CIUDAD_CODIGOS = {
    'Arequipa': '0001',
    'Ayacucho': '0002',
    'Cajamarca': '0003',
    'Chiclayo': '0004',
    'Chimbote': '0005',
    'Cusco': '0006',
    'Huancayo': '0007',
    'Huanuco': '0008',
    'Huaraz': '0009',
    'Ica': '0010',
    'Iquitos': '0011',
    'Norte Chico': '0012',
    'Piura': '0013',
    'Pucallpa': '0014',
    'Puno': '0015',
    'Tacna': '0016',
    'Tarapoto': '0017',
    'Trujillo': '0018',
    'Puerto Maldonado': '0019',
    'Chincha': '0020',
}

class DocumentalMobilityExpediture(models.Model):
    _name = 'documental.mobility.expediture'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Documental Mobility Expediture'
    _order = 'id desc'

    name = fields.Char(copy=False, default=lambda self: _('New'), required=True)
    state = fields.Selection(string='State', selection=state, default='draft', tracking=True)
    used = fields.Boolean(default=False, string='Used')
    requirement_id = fields.Many2one(comodel_name='documental.requirements', string='Used in')
    budget_id = fields.Many2one(comodel_name="budget", string="Budget Number")
    cost_center_id = fields.Many2one(comodel_name="cost.center", string="CC Number", related="budget_id.cost_center_id")
    period = fields.Selection(selection=months, string='Period', default='enero', tracking=True)
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", default=lambda self: self.env.user.employee_id)
    full_name = fields.Many2one(comodel_name="res.users", string='Full Name', default=lambda self: self.env.user)

    city_id = fields.Many2one('res.province', compute='compute_city', string='Ciudad', store=True)
    codigo_city = fields.Char(string='Código de Ciudad', compute='_compute_codigo_city', store=True)

    dni = fields.Char(string='DNI', default=get_default_dni)
    date = fields.Datetime(string='Date', default=fields.Datetime.now)

    mobility_detail_ids = fields.One2many('documental.mobility.expediture.detail', 'documental_mobility_id', string='Mobility Expediture Details')
    restrict_mobility_detail_ids = fields.One2many('documental.mobility.expediture.detail', 'documental_mobility_id', string='Mobility Expediture Details')

    amount_total = fields.Float(string='Amount Total', compute='compute_amount_total', store=True, tracking=True)

    petitioner_signature = fields.Binary(string="Petitioner", copy=False, attachment=True)
    is_petitioner_signed = fields.Boolean(default=False, tracking=True, copy=False)
    petitioner_signed_on = fields.Datetime(string="Signed by petitioner on", tracking=True)

    executive_signature = fields.Binary(string='Executive', copy=False, attachment=True)
    is_executive_signed = fields.Boolean(default=False, tracking=True, copy=False)
    executive_signed_on = fields.Datetime(string="Signed by executive on", tracking=True)

    # --------------------------
    # Helpers internos
    # --------------------------
    def _safe_display_name(self, user):
        """
        Devuelve un nombre amigable para firma:
        alias_name > partner.name > user.name
        Lanza UserError si no hay forma de obtener un nombre.
        """
        if not user:
            raise UserError(_("No user provided for signature."))

        alias_name = ustr(getattr(getattr(user, "partner_id", False), "alias_name", "") or "").strip()
        if alias_name:
            return alias_name

        partner_name = ustr(getattr(getattr(user, "partner_id", False), "name", "") or "").strip()
        if partner_name:
            return partner_name

        user_name = ustr(getattr(user, "name", "") or "").strip()
        if user_name:
            return user_name

        raise UserError(_("The user has no name or alias configured to generate a signature."))

    def _safe_budget_responsible_name(self):
        """
        Obtiene el nombre del responsable desde budget_id con validación.
        """
        if not self.budget_id:
            raise UserError(_("Set a Budget before signing."))
        if not self.budget_id.responsible_id:
            raise UserError(_("The Budget has no Responsible user set."))
        return self._safe_display_name(self.budget_id.responsible_id)

    # --------------------------
    # Computes / defaults
    # --------------------------
    @api.depends('full_name')
    def compute_city(self):
        for record in self:
            partner = record.full_name.partner_id if record.full_name else False
            record.city_id = partner.province_id.id if (partner and partner.province_id) else False

    @api.model
    def default_get(self, fields_list):
        defaults = super(DocumentalMobilityExpediture, self).default_get(fields_list)
        user_partner = self.env.user.partner_id
        if user_partner and user_partner.province_id:
            defaults['city_id'] = user_partner.province_id.id
        return defaults

    @api.depends('city_id')
    def _compute_codigo_city(self):
        for record in self:
            if record.city_id:
                record.codigo_city = CIUDAD_CODIGOS.get(record.city_id.name, '')
            else:
                record.codigo_city = ''

    @api.depends('mobility_detail_ids.amount')
    def compute_amount_total(self):
        for mob in self:
            mob.amount_total = sum(mob.mobility_detail_ids.mapped('amount'))

    # (Esta función no alteraba campos; la dejo por compatibilidad)
    @api.depends('mobility_detail_ids.date')
    def compute_amount_partial(self):
        # Si en el futuro deseas calcular parciales por fecha, puedes hacerlo aquí.
        for mob in self:
            pass

    # --------------------------
    # Acciones
    # --------------------------
    def attach_files(self):
        attachments = []
        for line in self.mobility_detail_ids:
            if line.document_file:
                attach = {
                    'name': line.document_filename,
                    'datas': line.document_file,
                    'store_fname': line.document_filename,
                    'res_model': self._name,
                    'res_id': self.id,
                    'type': 'binary',
                }
                attachment = self.env['ir.attachment'].create(attach)
                attachments.append(attachment.id)
        return attachments

    def button_refused(self):
        self.write({
            'petitioner_signature': False,
            'is_petitioner_signed': False,
            'executive_signature': False,
            'is_executive_signed': False,
            'state': 'refused',
        })

    def button_petitioner_signature(self):
        for rec in self:
            rec.attach_files()
            rec.button_done()  # mantengo tu flujo original

            petitioner_name = rec._safe_display_name(rec.env.user)
            responsible_name = rec._safe_budget_responsible_name()

            petitioner_png_b64 = signature_generator(petitioner_name)
            executive_png_b64 = signature_generator(responsible_name)

            rec.write({
                'petitioner_signature': petitioner_png_b64,
                'is_petitioner_signed': True,
                'petitioner_signed_on': fields.Datetime.now(),

                'executive_signature': executive_png_b64,
                'is_executive_signed': True,
                'executive_signed_on': fields.Datetime.now(),

                'state': 'executive',
            })

    def button_executive_signature(self):
        for rec in self:
            exec_name = rec._safe_display_name(rec.env.user)
            exec_png_b64 = signature_generator(exec_name)

            rec.write({
                'executive_signature': exec_png_b64,
                'is_executive_signed': True,
                'executive_signed_on': fields.Datetime.now(),
                'state': 'done',
            })

    def button_intern_control_refuse(self):
        self.write({
            'executive_signature': False,
            'is_executive_signed': False,
            'executive_signed_on': False,
        })
        self.button_refused()

    def get_date_without_decimals(self):
        for rec in self:
            rec.date = rec.create_date

    def action_print_pdf(self):
        return self.env.ref('mkt_documental_managment.report_documental_mobility_expediture').report_action(self)

    def _get_report_documental_mobility_expediture_base_filename(self):
        self.ensure_one()
        return _('Mobility Expediture - %s') % (self.name or '')

    def draft(self):
        self.state = 'draft'

    def button_done(self):
        for rec in self.mobility_detail_ids:
            # Suma de montos del mismo usuario/fecha en otros registros no 'refused'
            total_day = sum(self.env['documental.mobility.expediture.detail'].search([
                ('user_id', '=', rec.user_id.id),
                ('date', '=', rec.date),
                ('state', '!=', 'refused')
            ]).mapped('amount'))
            if total_day > 45:
                raise ValidationError(_(
                    'The mobility must not exceed the maximum amount of 45. '
                    'On the date %s the maximum is exceeded.\n'
                    'Note: If you consider that in the %s Mobility Form you have not consumed more than 45 soles, '
                    'they may have been consumed in other records.'
                ) % (str(rec.date), rec.documental_mobility_id.name))

    @api.model
    def create(self, vals):
        """Genera el nombre del registro basado en la ciudad."""
        # Asegurar city_id
        if not vals.get('city_id'):
            user_ciudad = self.env.user.partner_id.province_id
            if user_ciudad:
                vals['city_id'] = user_ciudad.id
            else:
                raise ValidationError(_('Debe configurar una ciudad en el usuario antes de guardar.'))

        ciudad = self.env['res.province'].browse(vals.get('city_id'))

        if ciudad.name == 'Lima':
            vals['name'] = self.env['ir.sequence'].next_by_code('documental.mobility.expediture')
        else:
            sequence_code = 'documental.mobility.expediture.ciudad'
            codigo = CIUDAD_CODIGOS.get(ciudad.name, '')
            if not codigo:
                raise ValidationError(_('El código para la ciudad "%s" no está definido.') % ciudad.name)

            sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
            if not sequence:
                raise ValidationError(_('No se encontró una secuencia configurada para la ciudad "%s".') % ciudad.name)

            next_val = sequence._next()
            vals['name'] = f"PM-{fields.Date.today().year}-{codigo}-{next_val}"

        return super(DocumentalMobilityExpediture, self).create(vals)


class DocumentalMobilityExpeditureDetail(models.Model):
    _name = 'documental.mobility.expediture.detail'
    _description = 'documental mobility expediture detail'

    documental_mobility_id = fields.Many2one(
        comodel_name="documental.mobility.expediture", string='Documental Mobility', ondelete="cascade")
    sequence_handle = fields.Integer(string="Sequence handle")
    # Mejor: usar context_today para evitar eval en import-time
    date = fields.Date(string='Date', default=fields.Date.context_today)
    reason = fields.Char(string='Reason')
    origin_place = fields.Char(string="From")
    destiny = fields.Char(string='To')
    document_file = fields.Binary(string="File")
    document_filename = fields.Char(string="File Name")
    amount = fields.Float(string='Partial Amount', digits=(10, 2))
    partial_amount = fields.Float(string='Amount', compute='_compute_total_amount')
    rowspan_quant = fields.Integer(string='Rowspan Quantity', compute='_compute_total_amount', store=True)
    user_id = fields.Many2one(comodel_name="res.users", related="documental_mobility_id.full_name", store=True)
    state = fields.Selection(related='documental_mobility_id.state', string="State", store=True)

    @api.depends('date', 'documental_mobility_id', 'documental_mobility_id.mobility_detail_ids.amount')
    def _compute_total_amount(self):
        for rec in self:
            if not rec.documental_mobility_id or not rec.date:
                rec.rowspan_quant = 0
                rec.partial_amount = 0.0
                continue
            date_records = self.search([
                ('date', '=', rec.date),
                ('documental_mobility_id', '=', rec.documental_mobility_id.id),
            ])
            rec.rowspan_quant = len(date_records)
            rec.partial_amount = sum(date_records.mapped('amount'))
