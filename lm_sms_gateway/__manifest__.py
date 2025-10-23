{
    "name": "LabsMobile SMS Gateway",
    "summary": "Envío de SMS vía LabsMobile API (json/send)",
    "version": "17.0.1.0.0",
    "author": "Israel + ChatGPT",
    "license": "LGPL-3",
    "depends": ["base", "contacts"],
    "data": [
    "security/ir.model.access.csv",
    "views/res_config_settings_views.xml",
    "views/sms_views.xml",
    ],
    "external_dependencies": {"python": ["requests"]},
}