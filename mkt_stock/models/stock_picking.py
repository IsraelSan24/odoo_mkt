from odoo import _, api, fields, models


class Picking(models.Model):
    _inherit = 'stock.picking'

    guide_number = fields.Char(string="Guide Number", tracking=True)
    warehouse_keeper = fields.Many2one(comodel_name="res.partner", string="Warehouse Keeper", tracking=True)
