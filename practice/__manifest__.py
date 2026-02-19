# -*- coding: utf-8 -*-
{
    "name": "School Manangement",
    "summary": "A simple CRUD app for a school Manangement with permissions",
    "description": """
Long description of module's purpose
    """,
    "author": "OVIETA",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "module_category_administration",
    "version": "0.1",
    # any module necessary for this one to work correctly
    "depends": ["base"],
    # always loaded
    "data": [
        "security/security.xml",  # 1. Create Groups first
        "security/ir.model.access.csv",  # 2. Then Access Rights
        "security/security_rules.xml",  # 3. Then Record Rules
        "views/views.xml",  # 4. Finally, Views that use the groups
        "views/templates.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
