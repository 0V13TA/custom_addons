{
    'name': 'Remove Odoo from Base URL',
    'version': '1.0',
    'category': 'Technical',
    'summary': 'Removes /odoo prefix from URLs',
    'description': """
        This module removes the /odoo prefix from all URLs in your Odoo instance.
        It overrides the URL routing to strip /odoo from paths.
    """,
    'author': 'Binit Nepal',
    'website': 'https://binitnepal.com.np',
    'depends': ['base', 'web'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'remove_odoo_url/static/src/js/prevent_odoo_redirect.js',
        ],
    },
    'installable': True,
    'auto_install': False,
    'application': False,
    'post_init_hook': 'post_init_hook',
}
