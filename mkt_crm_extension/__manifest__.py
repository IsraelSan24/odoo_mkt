{
    'name': 'CRM Extension',
    'version': '1.0.0',
    'category': 'mkt',
    'summary': 'Extiende el CRM con el campo Marca',
    'author' : 'Mario Lopez - Marketing Alterno',
    'license': 'LGPL-3',
    'depends': ['crm'],  # Dependemos del módulo CRM
    'data': [
        'views/crm_lead_view.xml',  # Vista donde se añadirá el campo Marca
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
