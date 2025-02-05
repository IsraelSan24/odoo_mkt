{
    'name':'Budget Quotation',
    'summary':'''
        Quotation of budget with source in settlements.
    ''',
    'version':'1.0.0',
    'category':'mkt',
    'author':'Aaron Ilizarbe - Marketing Alterno',
    'license': 'AGPL-3',
    'depends':[
        'base',
        'mail',
    ],
    'data':[
        'security/security.xml',
        'security/ir_model_access.xml',

        'data/ir_sequence.xml',

        'views/quotation_budget_views.xml',
        'views/menu_views.xml',
    ],
    'installable':True,
    'auto_install':False,
}