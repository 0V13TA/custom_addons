# -*- coding: utf-8 -*-
{
    'name': "enterprise_theme",

    'summary': "To change to the enterprise theme",

    'description': """
Long description of module's purpose
    """,

    'author': "Freelance",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/backend_layout.xml',
        'views/dashboard_template.xml',
        'views/webclient_templates.xml',
        'views/login_template.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
             'enterprise_theme/static/src/scss/style.scss',
             'enterprise_theme/static/src/scss/apps.scss',
            'enterprise_theme/static/src/js/theme_loader.js',
            'enterprise_theme/static/src/js/active_menu_highlight.js',
            'enterprise_theme/static/src/scss/table.scss',
            'enterprise_theme/static/src/scss/login_style.scss',
            'enterprise_theme/static/src/js/custom_user_menu.js',
            
        ],
    },
    'installable': True,
    'application': True,
}

