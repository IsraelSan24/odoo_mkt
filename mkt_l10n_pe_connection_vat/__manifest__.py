{
    'name': 'Vat connection',
    'version': '1.0.0',
    'summary': 'RUC and DNI consult for contacts',
    'category': 'mkt',
    'author': 'Aaron Ilizarbe - Marketing Alterno',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'l10n_pe',
        'base_address_city',
    ],
    'data': [
        'views/res_partner.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}