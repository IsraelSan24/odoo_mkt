{
    'name':'HP Stock View',
    'summary':'Custom View for HP in Inventory',
    'version':'1.0.0',
    'author':'Aaron Ilizarbe - Marketing Alterno',
    'license':'AGPL-3',
    'depends':[
        'stock', 'product', 'mkt_report_formats', 'mkt_gallery'
    ],
    'data':[
        'security/security.xml',

        'wizard/stock_hp_report_wiz.xml',
        
        'views/report_stock_hp_views.xml',
        'views/stock_move_hp_views.xml',
        'views/stock_menu_views.xml',

    ],
    'installable':True,
    'auto_install':False
}