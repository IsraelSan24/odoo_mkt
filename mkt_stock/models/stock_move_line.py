from odoo import _, api, fields, models

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    picking_guide_number = fields.Char(related="picking_id.guide_number", readonly=True)