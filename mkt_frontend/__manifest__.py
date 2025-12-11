{
    'name': 'MKT Frontend',
    'version': '1.0.0',
    'category': 'mkt',
    'summary': 'Diseños en general',
    'description': """
        Módulo personalizado que:
        - Mejora el diseño visual del formulario de login
        - Diseño profesional con colores personalizados
    """,
    'author' : 'Mario Lopez - Marketing Alterno',
    'license': 'LGPL-3',
    'depends': ['web','auth_signup'],
    'data': [
        'views/webclient_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'mkt_frontend/static/src/css/login.css',
            'mkt_frontend/static/src/css/reset_password.css',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}