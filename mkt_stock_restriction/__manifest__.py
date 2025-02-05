{
    'name':'Warehouse Domains',
    'summary':'Warehouse restrictions in stock',
    'version':'1.0.0',
    'author':'Aaron Ilizarbe - Marketing Alterno',
    'license':'AGPL-3',
    'catergory':'Warehouse',
    'depends':[
        'base','stock',
    ],
    'data':[
        'security/security.xml',
        'views/res_users_views.xml',
        'views/stock_picking_views.xml',
    ],
    'installable':True,
    'auto_install':False,
}