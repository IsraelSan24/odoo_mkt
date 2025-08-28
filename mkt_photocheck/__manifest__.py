{
    'name': 'Photocheck',
    'summary': 'Photocheck',
    'description': 'Photocheck',
    'version': '1.0.0',
    'category': 'mkt',
    'author' : 'Mario Lopez - Marketing Alterno',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'hr',
        'mail',
        'website',
        'mkt_res_partner_brand',
    ],
    'data': [
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',

        'data/ir_sequence.xml',
        'data/mail_template.xml',

        'report/photocheck_report.xml',
        'report/paperformat_data.xml',
        'report/ir_actions_report.xml',

        'views/photochceck_views.xml',
        'views/photocheck_brand_group_views.xml',
        'views/photocheck_supervisor_views.xml',
        'views/photocheck_job_views.xml',
        'views/photocheck_city_views.xml',
        'views/website_menu.xml',
        'views/menu_views.xml',
        
    ],
    # 'assets': {
    #     'web.assets_frontend': [
    #         # 'mkt_photocheck/static/src/js/brand_supervisor.js',
    #     ],
    # },
    'installable': True,
    'auto_install': False,
    'application': True,
}