{
    'name': 'Custom User',
    'summary': '''
        Create a new user with determinated restrictions which depends of its job
    ''',
    'version': '1.0.0',
    'author': 'Aaron Ilizarbe - Marketing Alterno',
    'license': 'AGPL-3',
    'depends':[
        'base',
        'stock',
        'account',
        'website',
        'hr',
        'hr_attendance',
        'hr_recruitment',
        'hr_contract',
        'sales_team'
    ],
    'data':[
        'security/ir_model_access.xml',

        'views/res_users_view.xml',
        'views/worker_job_views.xml',
    ],
    'installable':True,
    'auto_install':False,
}