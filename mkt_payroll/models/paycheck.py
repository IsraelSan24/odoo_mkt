from odoo import _, api, fields, models

class Paycheck(models.Model):
    _name = 'paycheck'
    _description = 'Paycheck'
    _order = 'id desc'

    name = fields.Char(copy=False, required=True, default=lambda self:_('New'))
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee')
    paycheck = fields.Binary(string='Paycheck')
    paycheck_filename = fields.Char(string='Filename')


    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('paycheck') or _('New')
        return super(Paycheck, self).create(vals)
