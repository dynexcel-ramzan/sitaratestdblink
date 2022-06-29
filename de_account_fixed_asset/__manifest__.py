# -*- coding: utf-8 -*-
{
    'name': "Fixed Asset",

    'summary': """
        Fixed Asset Register
        """,

    'description': """
        Fixed Asset Register
        1- Direct Fixed Asset
        2- AUC(Asset Under Construction)
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account_asset'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_asset_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
