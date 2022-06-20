# -*- coding: utf-8 -*-
{
    'name': "Dealer",

    'summary': """
            dealer application
        """,

    'description': """
            dealer application
        """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    
    'category': 'Contacts',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts','sales_team','sale','account','crm'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/contact_dealer_view.xml',
        'views/dealer_views.xml',
        'views/dealer_commission_rate_view.xml',
        'views/dealer_commission_line_view.xml',
        'views/sale_order_view.xml',
        'views/account_invoice_view.xml',
        'views/crm_sale_team_view.xml',
        'views/crm_lead_view.xml',
        'views/action.xml',
        'views/dealer_menus.xml',
        'views/res_partner.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}


