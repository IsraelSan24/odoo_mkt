
{
    'name': 'Gestion Documental MKT',
    'version': '1.2',
    'author': 'Arturo Gil Serpa',
    'category': 'Website',
    'depends': ['base','website', 'mail','web'],
    'license': 'AGPL-3',
    'data': [
        'views/templates.xml',
        'views/views.xml',
        'report/report-requerimiento.xml',
        'report/report-liquidacion.xml',
        'report/report-gastos.xml',
        'report/report-equipos.xml',
        'views/mail_template_requerimiento.xml',
        'views/mail_template_liquidacion.xml',
        'views/mail_template_gastos.xml',
        'views/mail_template_equipos.xml',
    ],
    'installable': True,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'gestion_documental_mkt/static/src/css/estilos_requerimiento.css',
            'gestion_documental_mkt/static/src/css/estilos_liquidacion.css',
            'gestion_documental_mkt/static/src/css/estilos_gastos.css',
            'gestion_documental_mkt/static/src/css/estilos_equipos.css',
            'gestion_documental_mkt/static/src/js/reporte.js',
        ],
    }

}