# -*- coding: utf-8 -*-
{
    'name': "vieterp_base",

    'summary': """
        vieterp_base
    """,

    'description': """
        vieterp_base
    """,

    'author': "VietERP / Sang",
    'website': "http://www.vieterp.net",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'VietERP',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'web',
    ],

    # always loaded
    'data': [
        'views/web_assets.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}