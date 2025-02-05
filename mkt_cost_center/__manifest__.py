{
    'name': 'Cost Center',
    'summary': 'Cost Center',
    'version': '1.0',
    'category': 'mkt',
    'author': 'Aaron Ilizarbe',
    'license': 'LGPL-3',
    'depends': [
        'mail',
        'mkt_res_province',
        'mkt_res_partner_brand',
    ],
    'data': [
        'security/ir.model.access.csv',
        
        'views/cost_center_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}