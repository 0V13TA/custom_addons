{
    'name': 'EnterpriseOne Accounting Dashboard',
    'version': '1.0',
    'category': 'Accounting',
    'summary': 'Simple income & expense dashboard inside Accounting app',
    'depends': ['base', 'web', 'account'],
    'author': 'Binit Nepal',
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_views.xml',
        
    ],
    'assets': {
        'web.assets_backend': [
            'https://code.jquery.com/jquery-3.6.0.min.js',
            'enterpriseone_account_dashboard/static/lib/chart.min.js',
            'enterpriseone_account_dashboard/static/src/js/dashboard.js',
            'enterpriseone_account_dashboard/static/src/xml/dashboard_template.xml',
            'enterpriseone_account_dashboard/static/src/css/dashboard.css',
        ],
       
    },
    'installable': True,
    'application': False,  # Integrates into existing Accounting app
    'auto_install': False,
}