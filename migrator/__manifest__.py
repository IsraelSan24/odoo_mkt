{
    'name': 'Migrator',
    'summary': 'Migrator',
    'version': '1.0',
    'author': 'Aaron Ilizarbe',
    'license': 'LGPL-3',
    'depends': [
        'mkt_documental_managment',
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/self_migrator_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}