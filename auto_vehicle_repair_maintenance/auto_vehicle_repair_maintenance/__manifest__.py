# -*- coding: utf-8 -*-
{
    'name': 'Vehicle Maintenance Workshop',
    'version': '18.0.1.0.0',
    'category': 'Services',
    'summary': 'Complete vehicle repair and maintenance management system',
    'description': """
Auto Vehicle Repair and Maintenance Module
=========================================

This module manages the full lifecycle of vehicle repair and maintenance operations:

* Vehicle Management
  - Record and manage all customer vehicles
  - Track vehicle details (make, model, VIN, license plate, year)
  - Link vehicles to customers/owners
  - View complete repair and maintenance history

* Inspection Management
  - Perform and log vehicle inspections
  - Record inspection findings and notes
  - Assign mechanics/technicians

* Quotation Management
  - Create repair quotations based on inspections
  - Track quotation amounts
  - Request customer approval

* Work Order Management
  - Track repair work progress
  - Assign mechanics to jobs
  - Record work descriptions and notes
  - Monitor start and end dates

* Approval Workflow
  - Customer approval process
  - State-based workflow (Inspection → Quotation → Approval → Work Order → Done)

* Maintenance Scheduling
  - Automatic maintenance record creation
  - Periodic maintenance intervals (1, 3, 6, 12 months)
  - Next maintenance date calculation
  - Maintenance tracking and reminders

Key Features:
-------------
* Complete vehicle lifecycle management
* Inspection to finalization workflow
* Quotation and approval system
* Work order tracking
* Automatic maintenance scheduling
* Role-based access control (Manager, Mechanic, Receptionist)
* Comprehensive reporting and history tracking
    """,
    'author': 'Custom Development',
    'website': 'https://www.odoo.com',
    'icon': '/auto_vehicle_repair_maintenance/static/description/icon.png',
    'depends': [
        'base',
        'contacts',
        'hr',
        'sale',
        'product',
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security_groups.xml',
        'data/sequences.xml',
        'reports/inspection_report.xml',
        'reports/work_order_report.xml',
        'views/vehicle_views.xml',
        'views/inspection_views.xml',
        'views/work_order_views.xml',
        'views/maintenance_record_views.xml',
        'views/spare_part_views.xml',
        'views/sale_order_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}

