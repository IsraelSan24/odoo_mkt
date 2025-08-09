from odoo import _, api, fields, models
from datetime import datetime

state = [
    ('draft','Draft'),
    ('active','Active'),
    ('closed','Closed'),
    ('locked','Locked'),
    ('canceled','Canceled'),
]

class Budget(models.Model):
    _name = 'budget'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Budget'
    _order = 'id desc'

    months = [('enero','Enero'),('febrero','Febrero'),('marzo','Marzo'),
            ('abril','Abril'),('mayo','Mayo'),('junio','Junio'),
            ('julio','Julio'),('agosto','Agosto'),('septiembre','Septiembre'),
            ('octubre','Octubre'),('noviembre','Noviembre'),('diciembre','Diciembre')
    ]

    name = fields.Char(copy=False, default=lambda self: _('New'), required=True, string="Budget number")
    month = fields.Selection(selection=months)
    year = fields.Selection(selection=[(str(num), str(num)) for num in reversed(range(2019, (datetime.now().year) + 3 ))])
    partner_brand_id = fields.Many2one(comodel_name="res.partner.brand", string="Brand", required=True)
    my_month_year = fields.Char(string="Month/Year")
    year_month_id = fields.Many2one(comodel_name="year.month", string="Month & Year", store=True)
    user_id = fields.Many2one(comodel_name="res.users", string="User", default=lambda self: self.env.user)
    partner_id = fields.Many2one(comodel_name="res.partner", string="Customer", required=True)
    campaign_id = fields.Many2one(comodel_name="budget.campaign", string="Campaign", required=True)
    campaign_track = fields.Char(string="Campaign", compute="compute_track_field", store=True, tracking=True)
    cost_center_id = fields.Many2one(comodel_name="cost.center", string="CC Number", required=True)
    cost_center_track = fields.Char(string="Cost center", compute="compute_track_field", store=True, tracking=True)
    class_id = fields.Many2one(comodel_name="budget.class", string="Class", required=True)
    class_track = fields.Char(string="Class", compute="compute_track_field", store=True, tracking=True)
    executive_id = fields.Many2one(comodel_name="res.users", string="Executive", required=True)
    responsible_id = fields.Many2one(comodel_name="res.users", string="Responsible", required=True)
    max_amount = fields.Float(string="Max Amount")
    amount_total = fields.Float(compute='_compute_amount_total', string='Amount total')
    responsible_revision = fields.Boolean(default=False, string='Responsible revision', tracking=True)
    budget_line_ids = fields.One2many("budget.line", "budget_id", string="Budget Line")
    line_ids = fields.One2many('budget.line', 'budget_id', string='Budget line')
    state = fields.Selection(selection=state, default='draft', string="State", tracking=True)
    sequence_id = fields.Many2one(comodel_name="ir.sequence", string="Reference Sequence", copy=False)


    def _compute_amount_total(self):
        for rec in self:
            if rec.line_ids:
                rec.amount_total = sum(rec.line_ids.mapped('amount'))
            else:
                rec.amount_total = 0


    @api.depends('campaign_id','cost_center_id','class_id')
    def compute_track_field(self):
        for rec in self:
            if rec.campaign_id:
                rec.campaign_track = rec.campaign_id.name
            if rec.cost_center_id:
                rec.cost_center_track = rec.cost_center_id.code
            if rec.class_id:
                rec.class_track = rec.class_id.name


    @api.onchange('month','year')
    def _onchange_month_year(self):
        for record in self:
            if record.month and record.year:
                month_label = next((m[1] for m in record.months if m[0] == record.month), '')
                my_month_year = month_label + '/' + record.year
                record.my_month_year = my_month_year
                new_year_month = self.env['year.month'].search([('name','=',my_month_year)])
                if new_year_month:
                    record.year_month_id = new_year_month.id
                else:
                    y_m =  self.env['year.month'].create({
                        'year': record.year,
                        'month':record.month
                    })
                    record.year_month_id = y_m.id


    def action_view_settlement(self):
        settlement = self.env['documental.settlements'].search([('state', 'not in', ['draft', 'rejected']),('budget_id', '=', self.id)]).ids
        open_view_settlement = {
            'name': _('Settlements'),
            'view_mode': 'tree,form',
            'res_model': 'documental.settlements',
            'type': 'ir.actions.act_window',
            'domain': [('id','in',settlement)]
        }
        return open_view_settlement


    @api.onchange('cost_center_id')
    def onchange_customer(self):
        if self.cost_center_id:
            self.partner_id = self.cost_center_id.partner_id
            self.partner_brand_id = self.cost_center_id.partner_brand_id
            self.executive_id = self.cost_center_id.executive_id
            self.responsible_id = self.cost_center_id.responsible_id
        else:
            self.partner_id = False
            self.partner_brand_id = False
            self.executive_id = False
            self.responsible_id = False


    @api.model
    def create(self, vals):
        sequence_month_year = self.env['year.month'].browse(vals.get('year_month_id'))
        if vals.get('name', _('New')) == _('New'):
            if sequence_month_year.sequence_id:
                vals['name'] = sequence_month_year.sequence_id.next_by_id()
        return super(Budget, self).create(vals)