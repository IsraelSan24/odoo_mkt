from odoo import http
from odoo.http import request

class StockPickingReportController(http.Controller):

    @http.route('/report/url/<int:stock_picking_id>', type='http', auth='public', website=True, csrf=False)
    def stock_picking_report(self, stock_picking_id, username=None, password=None, **kwargs):
        stock_picking = request.env['stock.picking'].sudo().browse(stock_picking_id)
        if not stock_picking:
            return request.not_found()

        if username and password:
            if username == stock_picking.name and password == stock_picking.generated_password:
                values = {'stock_picking': stock_picking}
                return request.render('mkt_stock_picking_report.stock_picking_report_page', values)
            else:
                return request.render('mkt_stock_picking_report.invalid_credentials', {'stock_picking_id': stock_picking_id})
        else:
            return request.render('mkt_stock_picking_report.login_page', {'stock_picking_id': stock_picking_id})

    @http.route('/report/login', type='http', auth='public', website=True, csrf=False)
    def login(self, **kwargs):
        return request.render('mkt_stock_picking_report.login_page')