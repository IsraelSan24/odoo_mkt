{
    'name': 'Space Reservation',
    'version': '1.0',
    'category': 'Operations',
    'icon': '/mkt_roomreserves/static/description/icon.png',
    'summary': 'Module for scheduling and reservation of spaces',
    'depends': ['base', 'mail'],
    'data': [
        'security/space_security.xml',
        'security/ir.model.access.csv',
        'views/space_room_views.xml',
        'views/space_booking_views.xml',
        'views/space_booking_item_views.xml',
        'views/menu_items.xml',
        'views/kanban_views.xml',
    ],
    'installable': True,
    'application': True,
}