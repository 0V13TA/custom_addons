# -*- coding: utf-8 -*-
{
    'name': 'Custom Branding',
    'version': '18.0.1.0.1',
    'category': 'Customization',
    'summary': 'Remove Odoo branding and replace with custom branding',
    'description': """
Custom Branding Module
=====================
This module removes all Odoo branding and replaces it with your custom branding:
- Database selection page logo and title
- Login page "Powered by Odoo" text
- POS receipt "Powered by Odoo" text
- Italian POS fiscal document footer (if installed)
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'depends': ['web', 'point_of_sale', 'base_setup'],
    'data': [
        'views/res_config_settings_views.xml',
        'views/templates.xml',
    ],
    'auto_load': False,
    'assets': {
        'web.assets_frontend': [
            'custom_branding/static/src/css/custom_branding.css',
        ],
        'point_of_sale.assets_prod': [
            'custom_branding/static/src/app/store/pos_store_override.js',
            'custom_branding/static/src/app/navbar/navbar.js',
            'custom_branding/static/src/app/screens/receipt_screen/receipt/order_receipt.xml',
            'custom_branding/static/src/app/screens/receipt_screen/receipt/receipt_header/receipt_header.xml',
            'custom_branding/static/src/app/screens/login_screen/login_screen.xml',
            'custom_branding/static/src/app/navbar/navbar.xml',
            'custom_branding/static/src/app/customer_display/customer_display_template.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}

