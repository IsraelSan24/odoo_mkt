{
    'name': 'Blacklist Verification',
    'version': '1.0.0',
    'category': 'mkt',
    'summary': 'Verificación pública de contactos en lista negra',
    'description': """
        Módulo para verificar si un contacto está en lista negra
        - Búsqueda por VAT/DNI/RUC
        - Búsqueda por nombre o email
        - Vista pública sin autenticación
    """,
    'author': 'Mario López',
    'website': 'https://www.marketing-alterno.com',
    'depends': ['base', 'website', 'contacts', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        "security/security.xml",
        'views/res_partner_views.xml',
        'views/blacklist_templates.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'mkt_blacklist/static/src/css/blacklist.css',
            'mkt_blacklist/static/src/js/blacklist.js',
        ],
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}