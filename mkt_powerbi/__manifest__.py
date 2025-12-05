{
    'name': 'PowerBI Reports View',
    'version': '15.0.1.0',
    'summary': 'Embed Power BI Reports directely into a form.',
    'description': '''
    This module allows embbeding Power BI reports via iframe directely in a form view.
    It supports access control to each report form and URL configuration.
    ''',
    'category': 'Tools',
    'author': 'Alexander Burgos - Marketing Alterno',
    'depends': ['base'],
    'icon': '/mkt_powerbi/static/description/icon.png',
    'assets': {
        'web.assets_backend': [
            'mkt_powerbi/static/src/css/powerbi.css'
        ]
    },
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',

        'views/powerbi_report_views.xml',
        'views/powerbi_report_menus.xml'
    ],
    "installable": True,
    'application': True,
    'license': 'LGPL-3'
}