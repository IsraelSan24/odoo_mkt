from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)

class BudgetMmodify(models.Model):
    _name = 'budget.modify'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Budget modify'
    _order = 'id desc'

    name = fields.Char(readonly=True, default=lambda self:_('New'), string='Name', copy=False)
    description = fields.Char(required=True, string='Description')
    modify_type = fields.Selection(selection=[
        ('executive','Executive'),
        ('responsible', 'Responsible'),
        ('move_btwn_budget','Move between budget'),
        ('executive_revision','Executive revision')], required=True, string='Modify type')
    budget_ids = fields.Many2many(comodel_name='budget', string='Budgets')
    old_executive = fields.Many2one(comodel_name='res.users', string='Old executive', domain="[('id','in',current_executive_ids)]")
    new_executive = fields.Many2one(comodel_name='res.users', string='New executive')
    current_executive_ids = fields.Many2many(comodel_name='res.users', compute='compute_budget_executives')
    old_budget_id = fields.Many2one(comodel_name='budget', string='Old budget')
    budget_line_ids = fields.One2many(related='old_budget_id.budget_line_ids', string='Budget line')
    lock_budget_line_ids = fields.One2many(related='old_budget_id.line_ids', string='Budget line')
    revision_executive_id = fields.Many2one(comodel_name='res.users', string='Executive')
    new_budget_id = fields.Many2one(comodel_name='budget', string='New budget')
    executive_revision = fields.Boolean(default=False, string='Executive revision')
    state = fields.Selection(selection=[('draft','Draft'),
                                        ('modified','Modified')], default='draft', string='State')
    is_reverted = fields.Boolean(default=False, string='Reverted')

    partner_brand_id = fields.Many2one('res.partner.brand', string='Brand (optional)')

    old_responsible = fields.Many2one(
        'res.users', string='Old responsible',
        domain="[('id','in',current_responsible_ids)]"
    )
    new_responsible = fields.Many2one('res.users', string='New responsible')
    current_responsible_ids = fields.Many2many(
        'res.users', compute='compute_budget_responsibles', string='Current responsibles'
    )

    def revert_executive_modify(self):
        if self.modify_type == 'executive' and self.state == 'modified':
            new_modify = self.env['budget.modify'].create({
                'description': 'Revertion of %s' % ( self.name ),
                'modify_type': 'executive',
                'old_executive': self.new_executive.id,
                'new_executive': self.old_executive.id,
                'budget_ids': [(4, budget_id.id) for budget_id in self.budget_ids]
            })
            self.is_reverted = True
            new_modify.modify_executive_budget()


    def modify_responsible_revision(self):
        for budget in self.budget_ids:
            budget.responsible_revision = self.executive_revision
        self.state = 'modified'


    @api.onchange('modify_type')
    def _onchange_modify_type(self):
        if self.modify_type == 'executive':
            self.old_budget_id = False
            self.new_budget_id = False
        elif self.modify_type == 'move_btwn_budget':
            self.old_executive = False
            self.new_executive = False
        else:
            self.old_budget_id = False
            self.new_budget_id = False
            self.old_executive = False
            self.new_executive = False


    def modify_settlement_between_budget(self):
        for settlement in self.old_budget_id.budget_line_ids:
            values = {}
            if settlement.remove:
                values.update({
                    'budget_id': settlement.budget_id.id,
                    'documental_settlement_id': settlement.documental_settlement_id.id,
                    'date': settlement.date,
                    'document_type': settlement.document_type,
                    'document_file': settlement.document_file,
                    'document_filename': settlement.document_filename,
                    'document': settlement.document,
                    'reason': settlement.reason,
                    'amount': settlement.amount,
                    'settlement_name': settlement.settlement_name,
                    'settlement_detail_id': settlement.settlement_detail_id.id,
                })
                self.new_budget_id.budget_line_ids = [(0,0,values)]
                settle = settlement.documental_settlement_id
                rq_settle = settle.requirement_id
                settle.budget_id = self.new_budget_id.id
                settle.cost_center_id = self.new_budget_id.cost_center_id.id
                settle.campaign_id = self.new_budget_id.campaign_id.id
                rq_settle.budget_id = self.new_budget_id.id
                rq_settle.cost_center_id = self.new_budget_id.cost_center_id.id
                rq_settle.campaign_id = self.new_budget_id.campaign_id.id
                rq_settle.partner_id = self.new_budget_id.partner_id.id
                rq_settle.year_month_id = self.new_budget_id.year_month_id.id
                settlement.unlink()
        self.state = 'modified'


    def modify_executive_budget(self):
        for budget in self.budget_ids:
            budget.executive_id = self.new_executive
        self.state = 'modified'


    @api.onchange('old_executive','modify_type','revision_executive_id')
    def onchange_budgets(self):
        if self.old_executive:
            self.budget_ids = self.env['budget'].search([('executive_id','=',self.old_executive.id)]).ids
        if self.revision_executive_id:
            self.budget_ids = self.env['budget'].search([('executive_id','=',self.revision_executive_id.id)]).ids


    @api.depends('description','modify_type','budget_ids','old_executive')
    def compute_budget_executives(self):
        if self.description or self.modify_type or self.budget_ids or self.old_executive:
            executive_ids = self.env['budget'].search([('executive_id','!=',False)]).mapped('executive_id')
            self.current_executive_ids = executive_ids
        else:
            self.current_executive_ids = False

    
    @api.onchange('old_responsible', 'partner_brand_id')
    def _onchange_responsible_brand_fill_budgets(self):
        """Autollenar budgets al elegir responsable, limitado por marca si aplica."""
        for rec in self:
            # siempre limpia primero
            rec.budget_ids = [(5, 0, 0)]
            if not rec.old_responsible:
                continue

            domain = [('responsible_id', '=', rec.old_responsible.id)]
            if rec.partner_brand_id:
                domain.append(('partner_brand_id', '=', rec.partner_brand_id.id))

            rec.budget_ids = self.env['budget'].search(domain).ids


    @api.model
    def create(self, vals):
        if vals.get('name',_('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('budget.modify') or _('New')
        return super(BudgetMmodify, self).create(vals)


    def modify_responsible_budget(self):
        """
        Idéntico a modify_executive_budget pero para el Responsible.
        La marca (partner_brand_id) es opcional y aquí no es bloqueante:
        si deseas filtrar budgets por marca, hazlo antes de poblar budget_ids.
        """
        for rec in self:
            for budget in rec.budget_ids:
                budget.responsible_id = rec.new_responsible
            rec.state = 'modified'


    def revert_responsible_modify(self):
        """
        Crea un registro de budget.modify inverso para deshacer el cambio de responsible,
        idéntico a revert_executive_modify pero con Responsible.
        """
        for rec in self:
            # No dependemos de modify_type para no tocar tu selección original.
            if rec.state == 'modified' and rec.new_responsible and rec.old_responsible:
                new_modify = self.env['budget.modify'].create({
                    'description': _('Revertion of %s') % (rec.name),
                    # conservamos el mismo modify_type que traiga rec (no añadimos tipos nuevos)
                    'modify_type': rec.modify_type,
                    'old_responsible': rec.new_responsible.id,
                    'new_responsible': rec.old_responsible.id,
                    'partner_brand_id': rec.partner_brand_id.id if rec.partner_brand_id else False,
                    'budget_ids': [(4, b.id) for b in rec.budget_ids],
                })
                rec.is_reverted = True
                new_modify.modify_responsible_budget()


    @api.depends('description','modify_type','budget_ids','old_responsible')
    def compute_budget_responsibles(self):
        Budget = self.env['budget']
        responsibles = Budget.search([('responsible_id','!=',False)]).mapped('responsible_id')
        for rec in self:
            rec.current_responsible_ids = responsibles or self.env['res.users']
