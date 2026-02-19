# -*- coding: utf-8 -*-
{
    "name": "HR Parent Menu",
    "summary": "Groups all HR related menus under a single HR parent menu",
    "description": """
        This module creates a top-level 'HR' menu and moves related HR modules 
        such as Employees, Payroll, Leave, Attendance, Recruitment, Transfers, 
        Fleet, Resignation, Timesheets, Announcements, and Reminders under it.
    """,
    "author": "Your Name / Company",
    "website": "https://www.yourcompany.com",
    "category": "Human Resources",
    "version": "18.0.1.0.0",

    "depends": [
        "hr",
        "hr_payroll_community",
        "hr_attendance",
        "hr_holidays",
        "hr_timesheet",
        "fleet",
    ],

    "data": [
        "views/hr_parent_menu.xml",
    ],

    "installable": True,
    "application": True,
    "auto_install": False,
}
