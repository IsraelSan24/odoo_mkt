from odoo import _, api, fields, models

def get_default_tax(self):
    return self.env['tax.taxes'].search([('name','=','IGV(18%)')]).id


class SettlementLine(models.Model):
    _name = 'settlement.line'
    _description = 'Settlement line'

    name = fields.Char(string='Description')
    settlement_id = fields.Many2one(comodel_name='settlement', string='Settlement')
    service_type_id = fields.Many2one(related='settlement_id.service_type_id', string='Service', store=True)
    tax = fields.Selection(selection=[
        ('levied', 'Levied'),
        ('surcharge', 'Surcharge'),
        ('exonerated', 'Exonerated'),
    ], default='levied', string='Tax')
    tax_id = fields.Many2one(comodel_name='tax.taxes', default=get_default_tax, string='Tax')
    igv_included = fields.Boolean(default=True, string='Included IGV?')
    quantity = fields.Integer(string='Quantity')
    unit_price = fields.Float(digits=(10,3), string='Unit price')
    base_amount = fields.Float(compute='_compute_base_amount', string='Base amount', store=True)
    igv = fields.Float(compute='_compute_igv', string='IGV', store=True)
    amount = fields.Float(compute='_compute_amount', string='Amount', store=True)

    def compute_base_igv_amount(self):
        self._compute_base_amount()
        self._compute_igv()
        self._compute_amount()


    @api.depends('quantity','unit_price','igv_included','tax','tax_id')
    def _compute_base_amount(self):
        for rec in self:
            if rec.igv_included:
                if rec.tax == 'levied':
                    rec.base_amount = round( ( rec.quantity * rec.unit_price ) / ( 1 + ( rec.tax_id.percentage / 100 ) ), 3 )
                else:
                    rec.base_amount = rec.quantity * rec.unit_price
            else:
                if rec.tax == 'levied':
                    rec.base_amount = rec.quantity * rec.unit_price
                else:
                    rec.base_amount = rec.quantity * rec.unit_price


    @api.depends('quantity','unit_price','igv_included','tax','tax_id')
    def _compute_igv(self):
        for rec in self:
            if rec.igv_included:
                if rec.tax == 'levied':
                    rec.igv = round( ( ( rec.quantity * rec.unit_price ) / ( 1 + (rec.tax_id.percentage / 100) ) ) * ( rec.tax_id.percentage / 100 ), 3 )
                else:
                    rec.igv = 0.00
            else:
                if rec.tax == 'levied':
                    rec.igv = round( ( rec.quantity * rec.unit_price ) * ( rec.tax_id.percentage / 100 ), 3 )
                else:
                    rec.igv = 0.00


    @api.depends('quantity','unit_price','igv_included','tax','tax_id')
    def _compute_amount(self):
        for rec in self:
            if rec.igv_included:
                if rec.tax == 'levied':
                    rec.amount = rec.quantity * rec.unit_price
                else:
                    rec.amount = rec.quantity * rec.unit_price
            else:
                if rec.tax == 'levied':
                    rec.amount = round( ( rec.quantity * rec.unit_price ) + ( ( rec.quantity * rec.unit_price ) * ( rec.tax_id.percentage / 100 ) ), 3 )
                else:
                    rec.amount = rec.quantity * rec.unit_price
