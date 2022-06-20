# -*- coding: utf-8 -*-
{
    'name': "Property Management",

    'summary': """
        Property Management
        """,

    'description': """
        Property Management
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sale/Inventory',
    'version': '15.0.0.2',
    'sequence': 160,
    # any module necessary for this one to work correctly
    'depends': ['base','product','stock','sale','de_dealer','account'],

    # always loaded
    'data': [
        'security/property_security.xml',
        'security/ir.model.access.csv',
        'data/ir_server_data.xml',
        'wizard/assign_dealer_wizard.xml',
        'wizard/assign_token_wizard.xml',
        'wizard/generate_booking_wizard.xml',
        'views/menuitem_views.xml',
        'views/property_views.xml',
        'views/product_views.xml',
        'views/partner_views.xml',
        'views/premium_factor_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
