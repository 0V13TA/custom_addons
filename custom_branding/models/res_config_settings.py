# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Database Manager Settings
    database_page_logo = fields.Binary(
        string='Database Page Logo',
        related='company_id.database_page_logo',
        readonly=False,
        help='Logo displayed on the database selection page'
    )
    database_page_title = fields.Char(
        string='Database Page Title',
        related='company_id.database_page_title',
        readonly=False,
        help='Title displayed on the database selection page (browser tab)'
    )

    # Login Page Settings
    login_powered_by_text = fields.Char(
        string='Login Page "Powered by" Text',
        related='company_id.login_powered_by_text',
        readonly=False,
        help='Text to display at bottom of login page (leave empty to hide)'
    )
    login_powered_by_url = fields.Char(
        string='Login Page "Powered by" URL',
        related='company_id.login_powered_by_url',
        readonly=False,
        help='URL for the "Powered by" link on login page'
    )

    # POS Receipt Settings
    pos_receipt_footer_text = fields.Char(
        string='POS Receipt Footer Text',
        related='company_id.pos_receipt_footer_text',
        readonly=False,
        help='Text to display at bottom of POS receipts (leave empty to hide)'
    )
    pos_logo = fields.Binary(
        string='POS Logo',
        related='company_id.pos_logo',
        readonly=False,
        help='Logo displayed in POS interface and receipts (replaces company logo)'
    )
    pos_company_name = fields.Char(
        string='POS Company Name',
        related='company_id.pos_company_name',
        readonly=False,
        help='Company name displayed in POS interface and receipts (replaces company name)'
    )


