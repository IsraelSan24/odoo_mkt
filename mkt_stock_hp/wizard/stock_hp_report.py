from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import io as io
from io import BytesIO
import base64
from PIL import Image


import logging
_logger = logging.getLogger(__name__)

class StockHpReport(models.TransientModel):
    _name = 'stock.hp.report'
    _description = 'HP Stock Report'
    _inherit = ['report.formats']

    partner_id = fields.Many2one(comodel_name="res.partner", string="Partner")


    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')


    def _get_file_name(self, function_name, file_name=False):
        dic_name = super(StockHpReport, self)._get_file_name(function_name, file_name=_("Hp Stock"))
        return dic_name


    def resize_image_data(self, file_path, bound_width_height):
        im = Image.open(file_path)
        im.thumbnail(bound_width_height, Image.ANTIALIAS)
        im_bytes = BytesIO()
        im.save(im_bytes, format='PNG')
        return im_bytes

    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Stock HP'))

        style1 = {
            'font_color':'#3C839F',
            'align': 'center',
            'border': 1,
            'bold': True,
        }
        style2 = {
            'border': 1,
        }

        stl1 = workbook.add_format(style1)
        stl2 = workbook.add_format(style2)

        ws.set_column('A:A', 50)
        ws.set_column('B:B', 13)
        ws.set_column('C:C', 16)
        ws.set_column('D:D', 10)
        ws.set_column('E:E', 20)
        ws.set_column('F:F', 15)
        ws.set_column('G:G', 13)
        ws.set_column('H:H', 11)

        ws.write("A1:A1", _('PRODUCT'), stl1)
        ws.write("B1:B1", _('SERIE N°'), stl1)
        ws.write("C1:C1", _('CATEGORY'), stl1)
        ws.write("D1:D1", _('TYPE'), stl1)
        ws.write("E1:E1", _('UBICATION'), stl1)
        ws.write("F1:F1", _('ENTRIES'), stl1)
        ws.write("G1:G1", _('DEPARTURES'), stl1)
        ws.write("H1:H1", _('STOCK'), stl1)
        ws.autofilter('A1:H1')

        records = self._get_query()
        row = 1
        # product_image = self.env['product.template']
        for line in records:
            # ws.set_row(row, 90)
            product_name = self.env['product.product'].search([('id','=',line['pp_id'])]).mapped('product_tmpl_id').name
            # ws.write(row, 0, line['report_product'], stl2)
            ws.write(row, 0, product_name, stl2)
            ws.write(row, 1, line['report_lot'], stl2)
            # image_line = product_image.search([('name','=',line['report_product'])]).image_1920
            # if image_line:
            #     pre_image = io.BytesIO(base64.b64decode(image_line))
            #     ws.write(row, 2, '', stl2)
            #     bound_width_height = (240,90)
            #     image_data = self.resize_image_data(pre_image, bound_width_height)
            #     ws.insert_image(row, 2, "image.png", {
            #         'image_data': image_data,
            #         'x_offset': 10,
            #         'y_offset': 10,
            #         'object_position': 3,
            #     })
            # else:
            #     ws.write(row, 2, '', stl2)
            # ws.write(row, 2, '', stl2)
            ws.write(row, 2, line['report_category'], stl2)
            ws.write(row, 3, line['report_product_type'], stl2)
            ws.write(row, 4, line['report_location'], stl2)
            ws.write(row, 5, line['report_incoming_qty'], stl2)
            ws.write(row, 6, line['report_outgoing_qty'], stl2)
            ws.write(row, 7, line['report_stock'], stl2)
            row += 1


    def _get_query(self):
        query= """
            SELECT
                sq.id AS id,
                pp.id AS pp_id,
                pt.name AS report_product,
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
                sq.quantity AS report_stock
            FROM stock_quant AS sq
            INNER JOIN product_product AS pp ON pp.id=sq.product_id
            INNER JOIN product_template AS pt ON pt.id = pp.product_tmpl_id
            INNER JOIN product_category AS pc ON pc.id = pt.categ_id
            INNER JOIN stock_location AS sl ON sl.id = sq.location_id
            LEFT JOIN stock_production_lot AS spl ON spl.id = sq.lot_id
            WHERE sl.complete_name IN ('MKT/HP TRADE Magdalena', 'MKT/HP TRADE Chorrillos')
            GROUP BY sq.id, pt.name, spl.name, pc.name, pt.detailed_type, sl.name, sq.quantity, pp.id, sl.id
            ORDER BY pt.name
        """
        self._cr.execute(query)
        res_query = self._cr.dictfetchall()
        return res_query