# -*- coding: utf-8 -*-
{
    'name': "tuanhuy_lock_sale_purchase",

    'summary': """
        tuanhuy_lock_sale_purchase""",

    'description': """
        tuanhuy_lock_sale_purchase
    """,

    'author': "VietERP/Quy",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/popup_lock.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}