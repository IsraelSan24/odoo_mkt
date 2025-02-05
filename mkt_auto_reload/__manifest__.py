{
    'name': 'Auto Reloading Web',
    'version': '1.0',
    'category': 'mkt',
    'author': 'Aaron Ilizarbe - Marketing Alterno',
    'license': 'AGPL-3',
    'depends': [
        'base'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'assets': {
        'web.assets_backend': [
            'mkt_auto_reload/static/src/js/autoreload.js',
        ]
    }
}