from odoo import _,fields, models, api

state = [
    ('draft','Draft'),
    ('to_do','To Do'),
    ('done','Done'),
    ('refused','Refused')
]

status = [
    ('returned', 'Returned'),
    ('assigned', 'Assigned'),
    ('maintenance', 'In Maintenance'),
]

def get_default_country(self):
    return self.env['res.country'].search([('code', '=', 'PE')], limit=1).id

class EquipmentStatus(models.Model):
    _name = 'equipment.status'
    _description = 'Equipment Status'
    _order = 'id desc'
    _rec_name = 'name_code'

    name = fields.Char(string='Team Code', required=True)
    name_code = fields.Char(required=True, default=lambda self:_('New'), string='Name Code', readonly=True)
    equipment_id = fields.Many2one(comodel_name='maintenance.equipment', string='Team', required=True)
    equipment_name = fields.Char(related='equipment_id.name', string='Name', required=True)

    location = fields.Char(string='Location', related='equipment_id.location')
    category_id = fields.Many2one(comodel_name='maintenance.equipment.category', related='equipment_id.category_id', string='Equipment Category', tracking=True)
    partner_brand_id = fields.Many2one(comodel_name='res.partner.brand', related='equipment_id.partner_brand_id', string='Brand')
    model = fields.Char(string='Model', related='equipment_id.model')
    serial_no = fields.Char(string='Serial number', related='equipment_id.serial_no')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Assigned Employee', related='equipment_id.employee_id')

    ram = fields.Char(string='RAM', related='equipment_id.ram')
    processor = fields.Char(string='Processor', related='equipment_id.processor')
    operating_system = fields.Char(string='Operating System', related='equipment_id.operating_system')
    screen = fields.Char(string='Screen', related='equipment_id.screen')
    disk = fields.Char(string='Disk', related='equipment_id.disk')
    observation = fields.Char(string="Observation")

    country_id = fields.Many2one(comodel_name='res.country', default=get_default_country, string='Country')
    state_id = fields.Many2one(comodel_name='res.country.state', string='Province')
    city_id = fields.Many2one(comodel_name='res.city', string='City')
    district_id = fields.Many2one(comodel_name='l10n_pe.res.city.district', string='District')

    state = fields.Selection(selection=state, string='Report Status', default='draft')
    status = fields.Selection(selection=status, string="Equipment Status", default='maintenance')

    component_ids = fields.One2many('equipment.component', 'status_id', string='Components')

    photo_base = fields.Binary(string='Laptop Base Photo')
    photo_base_filename = fields.Char(string='Base File Name', store=True)

    photo_left_side = fields.Binary(string='Left Side Photo')
    photo_left_side_filename = fields.Char(string='Left Side File Name', store=True)

    photo_right_side = fields.Binary(string='Right Side Photo')
    photo_right_side_filename = fields.Char(string='Right Side File Name', store=True)

    # photo_open = fields.Binary(string='Laptop Open Photo')
    # photo_open_filename = fields.Char(string='Open File Name', store=True)

    photo_open_screen = fields.Binary(string='Laptop Open Screen Photo')
    photo_open_screen_filename = fields.Char(string='Laptop Open Screen File Name', store=True)

    photo_open_keyboard = fields.Binary(string='Laptop Open Keyboard Photo')
    photo_open_keyboard_filename = fields.Char(string='Laptop Open Keyboard File Name', store=True)

    photo_closed = fields.Binary(string='Laptop Closed Photo')
    photo_closed_filename = fields.Char(string='Closed File Name', store=True)

    photo_charger = fields.Binary(string='Charger Photo')
    photo_charger_filename = fields.Char(string='Loader File Name', store=True)

    photo_additional = fields.Binary(string='Additional Photo')
    photo_additional_filename = fields.Char(string='Additional File Name', store=True)

    photo_additional_new = fields.Binary(string='Additional new Photo')
    photo_additional_new_filename = fields.Char(string='Additional File Name', store=True)
    
    photo_microphone = fields.Binary(string='Microphone Photo')
    photo_microphone_filename = fields.Char(string='Microphone File Name', store=True)
    
    photo_keyboard = fields.Binary(string='Keyboard Photo')
    photo_keyboard_filename = fields.Char(string='File Name Keyboard', store=True)
    
    photo_camera = fields.Binary(string='Camera Photo')
    photo_camera_filename = fields.Char(string='File Name Camera', store=True)

    active = fields.Boolean(string='Active', default=True, tracking=True)


    def button_to_do(self):
        self.write({
            'state': 'to_do',
        })


    def button_draft(self):
        self.state = 'draft'


    def button_done(self):
        self.write({
            'state': 'done',
        })


    def button_refuse(self):
        self.write({
            'state': 'refused',
        })


    def print_report(self):
        self.ensure_one()
        return self.env.ref('mkt_maintenance.report_equipment_status').report_action(self, data={
            'user': self.env.user,
        })

    @api.model
    def create(self, vals):
        if vals.get('name_code',_('New')) == _('New'):
            vals['name_code'] = self.env['ir.sequence'].next_by_code('equipment.status') or _('New')
        return super(EquipmentStatus, self).create(vals)