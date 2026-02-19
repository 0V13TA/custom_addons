# -*- coding: utf-8 -*-

from odoo import models


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _load_pos_data_fields(self, config_id):
        """Override to include custom branding fields in company data loaded in POS"""
        import logging
        _logger = logging.getLogger(__name__)
        
        fields = super()._load_pos_data_fields(config_id)
        # Add custom branding fields to company fields
        custom_fields = ['pos_receipt_footer_text', 'pos_logo', 'pos_company_name']
        for field in custom_fields:
            if field not in fields:
                fields.append(field)
        
        _logger.info("[Custom Branding] _load_pos_data_fields called, fields: %s", fields)
        return fields

