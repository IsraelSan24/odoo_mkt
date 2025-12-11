{
    'name': 'MKT Login Cleanup',
    'version': '1.0.0',
    'category': 'mkt',
    'summary': 'Limpia espacios en login y mejora diseño del formulario',
    'description': """
        Módulo personalizado que:
        - Elimina espacios en blanco del email y contraseña
        - Convierte el email a minúsculas automáticamente
        - Mejora el diseño visual del formulario de login
        - Diseño profesional con colores personalizados
    """,
    'author' : 'Mario Lopez - Marketing Alterno',
    'license': 'LGPL-3',
    'depends': ['web','auth_signup'],
    'data': [
    ],
    'assets': {
        'web.assets_frontend': [
            'mkt_login_cleanup/static/src/js/login.js',
            'mkt_login_cleanup/static/src/js/reset_password.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}