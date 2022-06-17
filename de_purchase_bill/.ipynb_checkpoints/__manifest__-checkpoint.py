# -*- coding: utf-8 -*-
{
    'name': "Purchase (Downpayment)",

    'summary': """
        Downpayment for purchase
        """,

    'description': """
        This module will add the downpayment functionality in purchase order
    """,



    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','purchase','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/purchase_advance_payment_inv.xml',
        'views/purchase_order_views.xml',
        'views/res_config_setting_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
