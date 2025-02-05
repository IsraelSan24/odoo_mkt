{
    'name':'Payroll',
    'summary':'''
        About payroll
    ''',
    'version':'1.0.0',
    'category':'mkt',
    'author':'Aaron Ilizarbe',
    'license':'AGPL-3',
    'depends':[
        'base',
        'mkt_recruitment',
    ],
    'data':[
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        
        'data/ir_sequence.xml',
        
        'views/paycheck_views.xml',
        'views/hr_employee.xml',
        'views/paycheck_portal_templates.xml',
        'views/menu_views.xml',
    ],
    'installable':True,
}
