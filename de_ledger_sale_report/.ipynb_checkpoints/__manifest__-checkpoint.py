# -*- coding: utf-8 -*-
{
    'name': "de_ledger_sale_report",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','de_sale_booking','de_property_payments','de_property','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'report/property_sale_report.xml',
        'report/partner_ledger_report.xml',
        'wizard/partner_ledger_wizard.xml',
        'wizard/property_sale_wizard.xml',
        'views/views.xml',
        'views/templates.xml',
        'views/product_category_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
