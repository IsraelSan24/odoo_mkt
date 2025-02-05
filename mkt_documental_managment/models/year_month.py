from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime

months = [('enero', 'Enero'), ('febrero', 'Febrero'),('marzo', 'Marzo'),
            ('abril', 'Abril'),('mayo', 'Mayo'),('junio', 'Junio'),
            ('julio', 'Julio'),('agosto', 'Agosto'),('septiembre', 'Septiembre'),
            ('octubre', 'Octubre'),('noviembre', 'Noviembre'),('diciembre', 'Diciembre')
]

class YearMonth(models.Model):
    _name = 'year.month'
    _description = 'My Year/Month table'
    _order = 'id desc'

    name = fields.Char(string="Year/Month", required=True, default=lambda self:_('New'), readonly=True)
    year = fields.Selection(selection=[(str(num), str(num)) for num in reversed(range(2019, (datetime.now().year) + 3 ))])
    month = fields.Selection(string="Month", selection=months)
    sequence_id = fields.Many2one(comodel_name="ir.sequence", string="Reference Sequence", copy=False)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'There is another record with the same month/year.')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = vals.get('month').capitalize() + '/' + vals.get('year')
            if 'sequence_id' not in vals or not vals['sequence_id']:
                if vals.get('year') and vals.get('month'):
                    month_number = str(months.index((vals['month'], vals['month'].capitalize())) +1).zfill(2)
                    vals['sequence_id'] = self.env['ir.sequence'].sudo().create({
                        'name': vals.get('month').capitalize() + '/' + vals.get('year') + _(' Sequence'),
                        'prefix': 'PT' + vals.get('year')[2:] + month_number + '-',
                        'padding': 3,
                    }).id
        return super().create(vals_list)
