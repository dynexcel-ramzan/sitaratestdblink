# -*- coding: utf-8 -*-
{
    'name': "Stock Billing",

    'summary': """
        Create Bill From Picking Document
        """,

    'description': """
        Create Bill From Picking Document
    """,

    'author': "Dynexccel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '14.0.1.4',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'account'],

    # always loaded
    'data': [
        #'data/ir_server_action.xml',
        'security/ir.model.access.csv',
        'wizard/create_invoice_wizard_view.xml',
        'views/stock_picking_views.xml',
        'views/account_move_views.xml',
    ],
    # only loaded in demonstration mode
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
