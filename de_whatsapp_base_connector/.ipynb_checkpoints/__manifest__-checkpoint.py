
{
    'name': '[10% OFF] WhatsApp Integration',
    'version': '14.0.0.2',
    'summary': 'Whatsapp messages',
    'description': """Odoo is a fully integrated suite of business modules that encompass the traditional ERP functionality.
        Use Odoo Whatsapp Integration to send messages on just one click.""",
    'category': 'Contacts',
    'author': 'Dynexcel',
    'maintainer': 'Dynexcel',
    'price': 99,
    'currency': 'EUR',
    'company': 'Dynexcel',
    'website': 'https://www.dynexcel.com',
    'depends': [
        'base','mail','base_setup', 'bus', 'web_tour','phone_validation'
        ],
    'data': [
        'data/customer_template.xml',
        'views/menu_item_views.xml',
        'wizard/message_compose_wizard.xml',
        'security/ir.model.access.csv',
        'views/message_template_view.xml',
        'views/whatsapp_message_log_views.xml',
        'views/res_config_setting_view.xml',
        'views/whatsapp_setting_view.xml',
       

    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': '',
}
