# -*- coding: utf-8 -*-
{
    'name': "landing_page",
    'summary': "Short (1 phrase/line) summary of the module's purpose",
    'description': """
Long description of module's purpose
    """,
    'author': "Aman Manandhar",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'web',],

    'data': [
        'views/dashboard_menu.xml',
        'views/dashboard_template.xml',
        'security/ir.model.access.csv',
    ],

    'qweb': [
        'landing_page/views/dashboard_template.xml',
    ],
     'assets':{
        'web.assets_backend': [
            'landing_page/static/src/js/custom_redirect.js',
             'landing_page/static/src/xml/dashboard_template.xml',
            'landing_page/static/src/scss/landing_page.scss',
        ],
     },
    'application': True,
    'installable': True,
}
