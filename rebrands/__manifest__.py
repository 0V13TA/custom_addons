
{
    'name': "rebrands",
    'version': '0.1',
    'category': 'Tools',
    'summary': "Replace Odoo 18 default logos and for rebranding into EnterpriseOne",
    'author': "BigFix Technologies",
    'depends': ['base', 'web'],
    'data': [
        # 'views/database_selector_overide.xml',
        'views/favicon_frontend_overide.xml',
        'views/app_icon_overides.xml',
        'views/nav_overide.xml',
        'views/footer_overide.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'rebrands/static/src/js/user_menu_overide.js',
            'rebrands/static/src/js/favicon_overide.js',
            'rebrands/static/src/js/database_selector_overide.js',
        ],
    },
    'installable': True,
    'application': True,
}
