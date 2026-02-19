# -*- coding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    # Database Manager Settings
    database_page_logo = fields.Binary(
        string='Database Page Logo',
        help='Logo displayed on the database selection page'
    )
    database_page_title = fields.Char(
        string='Database Page Title',
        default='Odoo',
        help='Title displayed on the database selection page (browser tab)'
    )

    # Login Page Settings
    login_powered_by_text = fields.Char(
        string='Login Page "Powered by" Text',
        help='Text to display at bottom of login page (leave empty to hide "Powered by" text)'
    )
    login_powered_by_url = fields.Char(
        string='Login Page "Powered by" URL',
        default='https://www.odoo.com',
        help='URL for the "Powered by" link on login page'
    )

    # POS Receipt Settings
    pos_receipt_footer_text = fields.Char(
        string='POS Receipt Footer Text',
        help='Text to display at bottom of POS receipts (leave empty to hide footer text)'
    )
    pos_logo = fields.Binary(
        string='POS Logo',
        help='Logo displayed in POS interface and receipts (replaces company logo)'
    )
    pos_company_name = fields.Char(
        string='POS Company Name',
        help='Company name displayed in POS interface and receipts (replaces company name)'
    )

