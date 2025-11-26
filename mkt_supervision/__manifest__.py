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
        'reports/hr_general_attendance_wizard.xml',
        
        "wizards/applicant_blacklist_confirm_wizard.xml",
        "wizards/partner_blacklist_check_wizard.xml",
        "wizards/applicant_set_contract_fields_wizard.xml",

        'views/stock_request_view.xml',
        'views/stock_request_line_view.xml',
        "views/stock_picking_views.xml",
        "views/hr_employee_view.xml",
        "views/hr_applicant_views.xml",
        "views/hr_departure_wizard_views.xml",
        "views/attendance_tareo_views.xml",
        "views/attendance_tareo_holiday_views.xml",
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
}
