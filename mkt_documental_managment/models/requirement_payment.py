from odoo import _, fields, models, api
from odoo.exceptions import ValidationError

class RequirementPayment(models.Model):
    _name = 'requirement.payment'
    _description = 'Requirement payment'

    requirement_id = fields.Many2one(comodel_name='documental.requirements', string='Requirement')
    requirement_state = fields.Selection(related='requirement_id.requirement_state', string='Requirement state')
    date_requested = fields.Date(string='Date requested', tracking=True)
    check_or_operation = fields.Selection(selection=[('check','Check'),('operation','Operation')], default='operation', string='Check/Operation', tracking=True)
    payment_bank_id = fields.Many2one(comodel_name="res.bank", string="Bank", domain="[('id','in',current_partner_bank_ids)]", default=lambda self: self._default_payment_bank_id(), tracking=True)
    bank_accounting_account = fields.Char(string='Bank accounting account')
    operation_number = fields.Char(string='Operation number', tracking=True)
    check_number = fields.Char(string='Check number', tracking=True)
    payment_date = fields.Date(string='Payment date', tracking=True)
    requirement_payroll_id = fields.Many2one(comodel_name='requirement.payroll', string='Payroll', tracking=True)
    amount = fields.Float(string='Amount', tracking=True)
    in_bank = fields.Boolean(default=False, copy=False, tracking=True)
    wrong_payment = fields.Boolean(default=False, copy=False, tracking=True)
    document_file = fields.Binary(string="Document File", attachment=True)
    document_filename = fields.Char(string="Filename")
    is_amount_editable = fields.Boolean(compute="_compute_is_amount_editable")
    is_administration_editable = fields.Boolean(compute="_compute_is_administration_editable")
    current_partner_bank_ids = fields.Many2many(
        comodel_name='res.bank', 
        compute='_compute_bank'
    )


    @api.constrains('in_bank')
    def _update_documental_requirement_in_bank(self):
        """Si cualquier RP tiene in_bank=True, marcar DR como True.
           Si todos los RP son False, marcar DR como False."""
        for record in self:
            if record.requirement_id:
                new_value = any(record.requirement_id.requirement_payment_ids.mapped('in_bank'))
                if record.requirement_id.in_bank != new_value:  # Solo escribir si es necesario
                    record.requirement_id.sudo().write({'in_bank': new_value})
                

    @api.depends('check_or_operation')
    def _compute_bank(self):
        bank_ids = self.env['res.partner'].browse(1).bank_ids.mapped('bank_id').ids
        self.current_partner_bank_ids = bank_ids


    def _default_payment_bank_id(self):
        bank = self.env['res.bank'].browse(4)
        if bank.exists():
            if self.requirement_id.amount_currency_type:
                currency = self.requirement_id.amount_currency_type.lower()
                if  currency == 'soles':
                    self.bank_accounting_account = '104103'
                elif currency == 'dolares':
                    self.bank_accounting_account = '104102'
            return bank.id
        return False


    @api.onchange('payment_bank_id')
    def onchange_payment_bank(self):
        for rec in self:
            if rec.payment_bank_id and rec.requirement_id.amount_currency_type:
                bank_name = (rec.payment_bank_id.name or '').lower()
                currency = (rec.requirement_id.amount_currency_type or '').lower()
                if "bcp" in bank_name and currency == 'soles':
                    rec.bank_accounting_account = '104101'
                elif "bcp" in bank_name and currency == 'dolares':
                    rec.bank_accounting_account = '104105'
                elif "bbva" in bank_name and currency == 'soles':
                    rec.bank_accounting_account = '104103'
                elif "bbva" in bank_name and currency == 'dolares':
                    rec.bank_accounting_account = '104102'
                else:
                    rec.bank_accounting_account = ''
            else:
                rec.bank_accounting_account = ''


    @api.depends("requirement_id.requirement_state")
    def _compute_is_amount_editable(self):
        for record in self:
            requirement = record.requirement_id  # Accede al modelo relacionado
            record.is_amount_editable = (
                requirement.requirement_state in ("draft", "refused") or
                (requirement.requirement_state == "administration" and 
                 self.env.user.has_group("mkt_documental_managment.documental_requirement_administration"))
            )


    @api.depends("requirement_id.requirement_state")
    def _compute_is_administration_editable(self):
        for record in self:
            requirement = record.requirement_id  # Accede al modelo relacionado
            record.is_administration_editable = (
                self.env.user.has_group("mkt_documental_managment.documental_requirement_administration") or
                requirement.requirement_state in ("draft", "refused")
            )


    @api.depends('document_file')
    def _compute_filename(self):
        for rec in self:
            if rec.document_file:
                rec.document_filename = f"payment_{rec.id}.pdf"  # Nombre básico para el archivo

    
    def attach_files(self):
        for rec in self:
            if rec.document_file:
                attachment = self.env['ir.attachment'].create({
                    'name': rec.document_filename,
                    'datas': rec.document_file,
                    'res_model': rec._name,
                    'res_id': rec.id,
                    'type': 'binary',
                })
                rec.message_post(body="File uploaded successfully", attachment_ids=[attachment.id])


    @api.model
    def default_get(self, fields_list):
        """ Calcula el valor por defecto de 'amount' basado en el total pendiente a pagar """
        defaults = super().default_get(fields_list)
        requirement_id = self._context.get('default_requirement_id')

        if requirement_id:
            requirement = self.env['documental.requirements'].browse(requirement_id)
            total_paid = sum(requirement.requirement_payment_ids.mapped('amount') or [0])
            remaining_amount = requirement.total_vendor - total_paid
            defaults['amount'] = max(0, remaining_amount)  # Si es negativo, asigna 0

        return defaults


    @api.model
    def create(self, vals):
        """ Crea el pago sin validaciones """
        return super().create(vals)