# -*- coding: utf-8 -*-
{
    'name': "Purchase Bill Advance",

    'summary': """
    Purchase Bill Advance
        """,

    'description': """
        Purchase Bill Advance
    """,

    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",

    'category': 'Dynexcel',
    'version': '14.0.0.3',

    # any module necessary for this one to work correctly
    'depends': ['de_purchase_bill'],

    # always loaded
    'data': [
        'views/account_move_views.xml',
    ],
  
}
