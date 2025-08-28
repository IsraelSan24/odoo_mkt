{
    'name': 'Supervisión',
    'version': '1.0',
    'summary': 'Supervisión de empleados',
    'description': 'Módulo para supervisar',
    'category': 'Human Resources',
    'author': 'Israel Santana',
    'depends': [
        'base', 
        'hr_attendance', 
        'report_xlsx', 
        'stock', 
        'hr_attendance_geolocation', 
        'hr',
        'hr_holidays',  
        'mkt_recruitment'
    ],
    'data': [
        'security/ir_module_category.xml',
        'security/res_groups.xml',
        'security/ir_rule.xml',
        'security/ir.model.access.csv',

        'reports/hr_attendance_wizard.xml',
        'reports/hr_attendance_tracking_wizard.xml',

        'views/stock_request_view.xml',
        'views/stock_request_line_view.xml',
        "views/stock_picking_views.xml",
        "views/hr_employee_view.xml",
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
