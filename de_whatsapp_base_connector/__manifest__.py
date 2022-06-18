# -*- coding: utf-8 -*-
#################################################################################
# Author      : Dynexcel (<www.dynexcel.com>)
# Copyright(c): 2015-Present Dynexcel
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################
{
    'name': 'Odoo WhatsApp Integration',
    'version': '14.0.0.2',
    'summary': 'Send Whatsapp Messages through Chat-Api',
    'description': """
    Whatsapp Integration:-
    - Can create multiple WhatsApp Accounts.
    - Can create dynamic templates for Whatsapp Messages.
    - Detail Logs of whatsapp Messages with delivery status report.
    - Maintain history of WhatsApp messages in chatter section.
	- Send Messages to partners from any of configured Account.
	- Send Message by using Template.
	- For more details please watch video and below screenshots.
    """,
    'category': 'Extra Tools',
    'author': 'Dynexcel',
    'maintainer': 'Dynexcel',
    'price': 29,
    'currency': 'USD',
    'company': 'Dynexcel',
    'website': 'https://www.dynexcel.com',
    'depends': [
        'base','mail','base_setup', 
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
    'images': ['static/description/banner.jpg'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
