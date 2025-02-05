{
    'name':'Maintenance',
    'summary':'Maintenance',
    'version':'1.0.0',
    'category':'mkt',
    'author':'Fabrizio Mori - Marketing Alterno',
    'license':'AGPL-3',
    'depends':[
        'base',
        'hr',
        'web',
        'mail',
        'website',
        'maintenance',
        'hr_maintenance',
        'mkt_res_partner_brand',
        'portal',
        'l10n_pe',
    ],
    'data':[
        'security/ir.model.access.csv',

        'data/ir_sequence.xml',

        'report/equipment_charge_report.xml',
        'report/equipment_status_report.xml',
        'report/paperformat.xml',
        'report/ir_actions_report.xml',

        'views/maintenance_views.xml',
        'views/equipment_status_views.xml',
        'views/website_menu.xml',
        'views/menu_views.xml',
    ],
    'assets':{
        'web.assets_frontend':[  
            'mkt_maintenance/static/src/js/ubigeo.js',
            'mkt_maintenance/static/src/js/autocomplete.js',
        ],
    },
    'installable':True,
    'application':False,
    'auto_install':False,
}