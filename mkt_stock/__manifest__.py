{
    'name':'Stock Modifications',
    'summary':"""
        Stock modifications and new features:
        - Some new fields in Stock
    """ ,
    'version':'1.0.0',
    'author':'Aaron Ilizarbe - Marketing Alterno',
    'license':'AGPL-3',
    'depends':[
        'base','stock',
    ],
    'data':[
        'views/stock_picking_view.xml',
        'views/stock_move_line_views.xml',
        'views/product_template_views.xml',
    ],
    'installable':True,
    'auto_install':False,
}