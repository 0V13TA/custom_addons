# -*- coding: utf-8 -*-
{
    'name': "H-Jubran ERP System - Phase 1 Core",
    'summary': "Foundational modules for H-Jubran ERP, focusing on Project Structure.",
    'description': """
        Implements Centralized Stage and Element Repository (PM-001) 
        for standardized project structures across the company.
    """,
    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'purchase', 'stock', 'sale'],

    # always loaded
    'data': [
        'security/purchase_request_groups.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'views/project_stage_views.xml',
        'views/project_element_views.xml',
        'views/project_structure_views.xml',
        'views/project_menu_views.xml',  # Must be loaded before master_data_views.xml
        'views/master_data_views.xml',
        'views/boq_summary_views.xml',
        
        'views/project_views.xml',
        
        'views/account_move_views.xml',
        'views/purchase_order_extends_views.xml',
        
        'views/h_jubran_purchase_request_views.xml',
        'views/petty_cash_views.xml',
        'views/purchase_menu_items.xml',
        'data/purchase_menu_reorder.xml'  # Must be loaded after purchase_menu_items.xml
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
}

