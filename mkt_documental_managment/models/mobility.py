from odoo import _, api, fields, models
from datetime import datetime
from odoo.exceptions import ValidationError
from odoo.addons.mkt_documental_managment.models.signature import signature_generator

state = [
    ('draft','Draft'),
    ('executive','Executive'),
    ('done','Done'),
    ('refused','Refused'),
]

def get_default_dni(self):
    vat = self.env.user.vat
    return vat

months = [('enero', 'Enero'), ('febrero', 'Febrero'), ('marzo', 'Marzo'),
          ('abril', 'Abril'), ('mayo', 'Mayo'),('junio', 'Junio'),
          ('julio', 'Julio'),('agosto', 'Agosto'),('septiembre', 'Septiembre'),
          ('octubre', 'Octubre'),('noviembre', 'Noviembre'),('diciembre', 'Diciembre'),
]

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
    _inherit = ["mail.thread", "mail.activity.mixin"]
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



    def compute_city(self):
        for record in self:
            partner = record.full_name.partner_id
            record.city_id = partner.province_id if partner else False

 
    @api.model
    def default_get(self, fields_list):
        defaults = super(DocumentalMobilityExpediture, self).default_get(fields_list)
        # Obtener la ciudad asociada al usuario actual
        user_partner = self.env.user.partner_id
        if user_partner and user_partner.province_id:
            defaults['city_id'] = user_partner.province_id.id
        return defaults

 
    @api.depends('city_id')
    def _compute_codigo_city(self):
        """Asigna el código correspondiente basado en el campo city_id."""
        for record in self:
            if record.city_id:
                record.codigo_city = CIUDAD_CODIGOS.get(record.city_id.name, '')
            else:
                record.codigo_city = ''
                
                
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


    def button_refused(self):
        self.write({
            'petitioner_signature': False, 
            'is_petitioner_signed': False,
            'executive_signature': False,
            'is_executive_signed': False,
            'state': 'refused',
        })


    def button_petitioner_signature(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        self.attach_files()
        self.button_done()
        self.write({
            'petitioner_signature': signature_generator(user_name),
            'is_petitioner_signed': True,
            'petitioner_signed_on': fields.Datetime.now(),
            'state': 'executive',
        })


    def button_executive_signature(self):
        alias_name = self.env.user.partner_id.alias_name
        user_name = alias_name if alias_name else self.env.user.name
        self.write({
            'executive_signature': signature_generator(user_name),
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


    @api.depends('mobility_detail_ids.date')
    def compute_amount_partial(self):
        for mob in self:
            dateOne = []
            amount_partial = 0.0
            for line in mob.mobility_detail_ids:
                dateOne.append(line.date)
                amount_partial += line.amount


    @api.depends('mobility_detail_ids.amount')
    def compute_amount_total(self):
        for mob in self:
            amount_total = 0.0
            for line in mob.mobility_detail_ids:
                amount_total += line.amount
                mob.update({
                    'amount_total': amount_total,
                })


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
            if sum( self.env['documental.mobility.expediture.detail'].search([('user_id','=',rec.user_id.id),('date','=',rec.date),('state','!=','refused')]).mapped('amount') ) > 45:
                raise ValidationError(_('The mobility must not exceed the maximum amount of 45. On the date %s the maximum is exceeded.\n'
                        'Note: If you consider that in the %s Mobility Form you have not consumed more than 45 soles, '
                        'they may have been consumed in other records.') % (str(rec.date), rec.documental_mobility_id.name))



    # @api.model
    # def _get_report_data(self):
    #     query = """
    #         SELECT
    #             rp.name AS partner,
    #             SUM(dmed.amount) AS amount,
    #             dmed.date AS date_line,
    #             dme.state AS state
    #         FROM documental_mobility_expediture_detail AS dmed
    #         INNER JOIN documental_mobility_expediture AS dme ON dme.id=dmed.documental_mobility_id
    #         LEFT JOIN res_users AS ru ON ru.id=dmed.create_uid
    #         LEFT JOIN res_partner AS rp ON rp.id=ru.partner_id
    #         -- WHERE dme.state != 'draft'
    #         GROUP BY rp.name, dmed.date, dme.state
    #         ORDER BY dmed.date
    #     """
    #     self._cr.execute(query)
    #     res_query = self._cr.dictfetchall()
    #     return res_query


    # @api.model
    # def create(self, vals):
    #     if vals.get('name', _('New')) == _('New'):
    #         vals['name'] = self.env['ir.sequence'].next_by_code('documental.mobility.expediture') or _('New')
    #     mobility = super(DocumentalMobilityExpediture, self).create(vals)
    #     return mobility
    
    @api.model
    def create(self, vals):
        """Genera el nombre del registro basado en la ciudad."""
        # Asignar city_id automáticamente si no está definido en vals
        if not vals.get('city_id'):
            user_ciudad = self.env.user.partner_id.province_id
            if user_ciudad:
                vals['city_id'] = user_ciudad.id
            else:
                raise ValidationError(_('Debe configurar una ciudad en el usuario antes de guardar.'))

        # Obtener el registro de city_id
        city_id = vals.get('city_id')
        ciudad = self.env['res.province'].browse(city_id)

        # Verificar si la ciudad es Lima
        if ciudad.name == 'Lima':
            # Usar directamente la secuencia configurada en el XML para Lima
            vals['name'] = self.env['ir.sequence'].next_by_code('documental.mobility.expediture')
        else:
            # Usar la secuencia configurada para provincias
            sequence_code = 'documental.mobility.expediture.ciudad'
            codigo = CIUDAD_CODIGOS.get(ciudad.name, '')
            if not codigo:
                raise ValidationError(_('El código para la ciudad "%s" no está definido.') % ciudad.name)

            # Obtener la secuencia correspondiente y generar el nombre
            sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
            if not sequence:
                raise ValidationError(_('No se encontró una secuencia configurada para la ciudad "%s".') % ciudad.name)

            next_val = sequence._next()
            vals['name'] = f"PM-{fields.Date.today().year}-{codigo}-{next_val}"

        return super(DocumentalMobilityExpediture, self).create(vals)


class DocumentalMobilityExpeditureDetail(models.Model):
    _name = 'documental.mobility.expediture.detail'
    _description = 'documental mobility expediture detail'

    documental_mobility_id = fields.Many2one(comodel_name="documental.mobility.expediture", string='Documental Mobility', ondelete="cascade")
    sequence_handle = fields.Integer(string="Sequence handle")
    date = fields.Date(string='Date', default=datetime.now())
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


    # @api.model
    # def _get_file_name(self, vals):
    #     return vals.get('document_filename') or _('File')


    def _compute_total_amount(self):
        dateList = []
        for rec in self:
            date_records = self.search([('date', '=', rec.date),('documental_mobility_id','=',self.documental_mobility_id.id)])
            total = sum(date_records.amount for date_records in date_records)
            dateList.append(len(date_records))
            rec.rowspan_quant = len(date_records)
            rec.partial_amount = total
