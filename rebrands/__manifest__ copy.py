# -*- coding: utf-8 -*-
{
    'name': "rebrands",
    'summary': "Replaces Odoo default logos with custom branding",
    'description': "Custom logo for login, database manager, and backend.",
    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Branding',
    'version': '1.0',

    'depends': ['web'],

    'assets': {
        'web.assets_backend': [
            'rebrands/static/src/css/rebrands.css',
        ],
        'web.assets_frontend': [
            'rebrands/static/src/css/rebrands.css',
            'rebrands/static/src/js/replace_logo.js',  
        ],
        'web.assets_database': [
            'rebrands/static/src/css/rebrands.css',
            'rebrands/static/src/js/replace_logo.js',  
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}