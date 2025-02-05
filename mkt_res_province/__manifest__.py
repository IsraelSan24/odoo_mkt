{
    'name': 'Province',
    'summary': 'Province',
    'version': '1.0',
    'category': 'mkt',
    'author': 'Aaron Ilizarbe',
    'license': 'LGPL-3',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/res_province_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}