from odoo import _, api, fields, models

class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.onchange('location_id')
    def _onchange_product_ubication(self):
        res = {}
        location = self.env['stock.quant'].search([('location_id','=',self.picking_id.location_id.id)])
        available_product_ids = location.mapped('product_id').ids
        if self.picking_id.location_id and self.picking_id.picking_type_id.code in ('internal', 'outgoing'):
            res['domain'] = {
                'product_id': [('id','in',available_product_ids)]
            }
        return res