from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
import io as io
import base64

import logging
_logger = logging.getLogger(__name__)

class StockSistReport(models.TransientModel):
    _name = 'stock.sist.report'
    _description = 'SIST Stock Report'
    _inherit = ['report.formats']

    def action_print_xlsx(self):
        return self.print_report_formats(function_name='xlsx', report_format='xlsx')
    

    def _get_file_name(self, function_name, file_name=False):
        dic_name = super(StockSistReport, self)._get_file_name(function_name, file_name=_("Sist Stock"))
        return dic_name

    def _get_datas_report_xlsx(self, workbook):
        ws = workbook.add_worksheet(_('Stock Sist'))

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
        ws.set_column('B:B', 20)
        ws.set_column('C:C', 15)
        ws.set_column('D:D', 15)
        ws.set_column('E:E', 15)
        ws.set_column('F:F', 15)
        ws.set_column('G:G', 15)

        ws.write("A1:A1", _('PRODUCT'), stl1)
        ws.write("B1:B1", _('SERIE N°'), stl1)
        ws.write("C1:C1", _('IMAGE'), stl1)
        ws.write("D1:D1", _('CATEGORY'), stl1)
        ws.write("E1:E1", _('TYPE'), stl1)
        ws.write("F1:F1", _('UBICATION'), stl1)
        ws.write("G1:G1", _('ENTRIES'), stl1)
        ws.write("H1:H1", _('DEPARTURES'), stl1)
        ws.write("I1:I1", _('STOCK'), stl1)
        ws.autofilter('A1:H1')

        stock_quant = self.env['stock.quant'].search([('location_id', 'in', ('SIST/HP','SIST/HP PRODUCCION','SIST/IMACO','SIST/MARKETING','SIST/MARKETING/LISTAS'))])

        stock_move_line = self.env['stock.move.line']

        row = 1
        for line in stock_quant:
            product_type = dict(line.product_id.product_tmpl_id._fields['detailed_type'].selection).get(line.product_id.product_tmpl_id.detailed_type)
            product_type_str = str(product_type)
            ws.set_row(row, 70)
            ws.write(row, 0, line.product_id.name, stl2)
            ws.write(row, 1, line.lot_id.name if line.lot_id else '', stl2)
            if line.product_id.image_1920:
                product_image = io.BytesIO(base64.b64decode(line.product_id.image_1920))
                ws.write(row, 2, '', stl2)
                ws.insert_image(row, 2, "image.png", {
                    'image_data': product_image,
                    'x_scale': 0.2,
                    'y_scale': 0.2,
                    'x_offset': 30,
                    'y_offset': 10,
                })
            else:
                ws.write(row, 2, '', stl2)
            ws.write(row, 3, line.product_id.product_tmpl_id.categ_id.name, stl2)
            ws.write(row, 4, _('%s') % (product_type_str), stl2)
            ws.write(row, 5, line.location_id.name, stl2)
            if line.lot_id:
                if len(stock_move_line.search([('location_dest_id','=',line.location_id.id),('product_id','=',line.product_id.id),('lot_id.name','=',line.lot_id.name),('picking_id.picking_type_id.code','!=','internal'),('picking_id.state','!=','cancel')]).mapped('qty_done')) != 0:
                    ws.write(row, 6, sum(stock_move_line.search([('location_dest_id','=',line.location_id.id),('product_id','=',line.product_id.id),('lot_id.name','=',line.lot_id.name),('picking_id.picking_type_id.code','!=','internal'),('picking_id.state','!=','cancel')]).mapped('qty_done')), stl2)
                else:
                    ws.write(row, 6, stock_move_line.search([('location_dest_id','in',('SIST/HP','SIST/HP PRODUCCION','SIST/IMACO','SIST/MARKETING','SIST/MARKETING/LISTAS')),('product_id','=',line.product_id.id),('lot_id.name','=',line.lot_id.name),('picking_id.picking_type_id.code','!=','internal'),('picking_id.state','!=','cancel')]).qty_done, stl2)

                if len(stock_move_line.search([('location_id','=',line.location_id.id),('product_id','=',line.product_id.id),('lot_id.name','=',line.lot_id.name),('picking_id.state','!=','cancel')]).mapped('qty_done')) != 0:
                    ws.write(row, 7, sum(stock_move_line.search([('location_id','=',line.location_id.id),('product_id','=',line.product_id.id),('lot_id.name','=',line.lot_id.name),('picking_id.state','!=','cancel')]).mapped('qty_done')), stl2)
                else:
                    ws.write(row, 7, stock_move_line.search([('location_id','=',line.location_id.id),('product_id','=',line.product_id.id),('lot_id.name','=',line.lot_id.name),('picking_id.state','!=','cancel')]).qty_done, stl2)

            else:
                if len(stock_move_line.search([('location_dest_id','=',line.location_id.id),('product_id','=',line.product_id.id),('picking_id.state','!=','cancel')]).mapped('qty_done')) != 0:
                    ws.write(row, 6, sum(stock_move_line.search([('location_dest_id','=',line.location_id.id),('product_id','=',line.product_id.id),('picking_id.state','!=','cancel')]).mapped('qty_done')), stl2)
                else:
                    ws.write(row, 6, stock_move_line.search([('location_dest_id','=',line.location_id.id),('product_id','=',line.product_id.id),('picking_id.state','!=','cancel')]).qty_done, stl2)

                if len(stock_move_line.search([('location_id','=',line.location_id.id),('product_id','=',line.product_id.id),('picking_id.state','!=','cancel')]).mapped('qty_done')) != 0:
                    ws.write(row, 7, sum(stock_move_line.search([('location_id','=',line.location_id.id),('product_id','=',line.product_id.id),('picking_id.state','!=','cancel')]).mapped('qty_done')), stl2)
                else:
                    ws.write(row, 7, stock_move_line.search([('location_id','=',line.location_id.id),('product_id','=',line.product_id.id),('picking_id.state','!=','cancel')]).qty_done, stl2)
            ws.write(row, 8, line.quantity, stl2)
            row += 1