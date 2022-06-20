# -*- coding: utf-8 -*-
{
    'name': "Property Payments",

    'summary': """
        Property Payments
        """,

    'description': """
        Property Payments
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '10.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale','de_property','account_batch_payment'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/register_pay_wizard.xml',
        'wizard/uniq_plot_resell_wizard.xml',
        'wizard/booking_discount_wizard.xml',
        'data/ir_server_action_data.xml',
        'views/account_batch_payment_views.xml',
        'wizard/register_installment_wizard.xml',
        'wizard/plot_resell_wizard.xml',
        'views/product_category_views.xml',
        'views/sale_order_views.xml',
        'views/account_payment_views.xml',
        'views/product_product_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
