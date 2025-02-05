from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class ProductTemplate(models.Model):
    _inherit = 'product.template'


    location_quantity = fields.Float(string="My quantity", compute="_compute_location_quantities")


    @api.depends(
        'product_variant_ids.qty_available',
        'product_variant_ids.virtual_available',
        'product_variant_ids.incoming_qty',
        'product_variant_ids.outgoing_qty',
    )
    def _compute_location_quantities(self):
        locations_ids = self.env.user.stock_location_ids.ids
        stock_quant = self.env['stock.quant']
        for rec in self:
            product_id = self.env['product.product'].search([('product_tmpl_id','=',rec.id)]).id
            rec.location_quantity = sum(stock_quant.search([('location_id','in',locations_ids),('product_id','=',product_id)]).mapped('quantity'))
