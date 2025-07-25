from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError

class ReportStockHP(models.Model):
    _name = 'report.stock.hp'
    _description = 'Query and fields for a tree view'
    _auto = False


    report_product_id = fields.Many2one(comodel_name="product.product", string="Product")
    report_product_template = fields.Char(string="Product", related="report_product_id.product_tmpl_id.name")
    report_lot = fields.Char(string="Serie")
    report_category = fields.Char(string="Category")
    report_product_type = fields.Char(string="Tipo")
    report_location = fields.Char(string="Location")
    report_incoming_qty = fields.Float(string="Incoming")
    report_outgoing_qty = fields.Float(string="Outgoing")
    report_stock = fields.Float(string="Stock")
    report_photo_loaded = fields.Boolean(string="Image?")


    def button_show_image(self):
        self.ensure_one()
        return {
            'name': _('Product Image'),
            'type': 'ir.actions.act_window',
            'res_model': 'gallery',
            'view_mode': 'form',
            'views': [(self.env.ref('mkt_gallery.view_gallery_form').id, 'form')],
            'res_id': self.env['gallery'].search([('product_id','=',self.report_product_id.product_tmpl_id.id)]).id,
            'target': 'new',
        }


    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(""" CREATE or REPLACE VIEW %s as (
            %s
            FROM %s AS sq
            %s
            )""" %(self._table, self._select(), self._from(), self._join()))


    def _select(self):
        select = """
            SELECT
                sq.id AS id,
                pt.name AS report_product,
                pp.id AS report_product_id,
                spl.name AS report_lot,
                pc.name AS report_category,
                pt.detailed_type AS report_product_type,
                sl.name AS report_location,
                COALESCE((
                    SELECT SUM(sml.qty_done)
                    FROM stock_move AS sm
                    INNER JOIN stock_move_line AS sml ON sml.move_id = sm.id
                    WHERE sml.product_id = pp.id
                    AND sm.location_dest_id = sl.id
                    AND (sq.lot_id IS NULL OR sml.lot_id IS NULL OR sml.lot_id = sq.lot_id)
                    AND sml.qty_done > 0
                    AND sm.state = 'done'
                ), 0) AS report_incoming_qty,
                COALESCE((
                    SELECT SUM(sml.qty_done)
                    FROM stock_move AS sm
                    INNER JOIN stock_move_line AS sml ON sml.move_id = sm.id
                    WHERE sml.product_id = pp.id
                    AND sm.location_id = sl.id
                    AND (sq.lot_id IS NULL OR sml.lot_id IS NULL OR sml.lot_id = sq.lot_id)
                    AND sml.qty_done > 0
                    AND sm.state = 'done'
                ), 0) AS report_outgoing_qty,
                sq.quantity AS report_stock,
                CASE WHEN EXISTS (
                    SELECT 1
                    FROM gallery
                    WHERE product_id = pt.id
                ) THEN TRUE ELSE FALSE END AS report_photo_loaded
        """
        return select


    def _from(self):
        return 'stock_quant'


    def _join(self):
        join = """
            INNER JOIN product_product AS pp ON pp.id=sq.product_id
            INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            INNER JOIN product_category AS pc ON pc.id = pt.categ_id
            INNER JOIN stock_location AS sl ON sl.id = sq.location_id
            LEFT JOIN stock_production_lot AS spl ON spl.id = sq.lot_id
            WHERE sl.complete_name IN ('MKT/HP TRADE Magdalena', 'MKT/HP TRADE Chorrillos')
            GROUP BY sq.id, pt.name, spl.name, pc.name, pt.detailed_type, sl.name, sq.quantity, pp.id, sl.id, pt.id
            ORDER BY pt.name
        """
        return join