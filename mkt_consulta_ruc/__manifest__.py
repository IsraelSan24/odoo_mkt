{
    'name':'RUC Consultant',
    'summary':'''
        Consultant RUC on SUNAT
    ''',
    'version':'1.0.0',
    'category':'MKT/Localization',
    'author':'Aaron Ilizarbe - Marketing Alterno',
    'license':'AGPL-3',
    'depends':['base'],
    'data':[
        'security/ir_model_access.xml',
        'views/consulta_ruc_views.xml',
        'views/menu_views.xml',
    ],
    'application':True,
    'installable':True,
    'auto_install':False,
}