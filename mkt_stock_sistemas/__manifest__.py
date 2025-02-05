{
    'name':'Sistemas Stock View',
    'summary':'Custom view for SISTEMAS in Inventory',
    'version':'1.0.0',
    'author':'Aaron Ilizarbe - Marketing Alterno',
    'license':'AGPL-3',
    'depends':[
        'stock','mkt_report_formats'
    ],
    'data':[
        'security/res_groups.xml',
        'security/ir_model_access.xml',

        'wizard/stock_sist_report_wiz.xml',

        'views/stock_quant_sist_views.xml',
        'views/stock_move_sist_views.xml',
        'views/stock_menu_views.xml',
    ],
    'installable':True,
    'application':True,
    'auto_install':False,
}