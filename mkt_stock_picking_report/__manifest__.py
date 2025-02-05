{
    'name': "mkt_stock_picking_report",
    'summary':'''
        Stock Picking Report
    ''',
    'version': '1.0.0',
    'author': 'Mario Lopez - Marketing Alterno',
    'license': 'AGPL-3',
    'category': 'mkt',
    'depends': [
        'base',
        'stock',
    ],
    'data': [
        'report/stock_picking_report_template.xml',
        'report/stock_picking_report_operations_template.xml',
        'report/paperformat.xml',
        'report/ir_actions_report.xml',

        'views/stock_picking_views.xml',
        'views/stock_picking_report_page.xml',
        'views/login_page.xml',
    ],
    'installable':True,
    'auto_install':False,
    'application':False,
}