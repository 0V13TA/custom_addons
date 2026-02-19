from odoo import models
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _get_default_lang(cls):
        """Ensure base.url doesn't contain /odoo"""
        result = super(IrHttp, cls)._get_default_lang()
        try:
            # Fix system parameter if it contains /odoo
            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url', '')
            if '/odoo' in base_url:
                new_base_url = base_url.replace('/odoo', '')
                request.env['ir.config_parameter'].sudo().set_param('web.base.url', new_base_url)
                request.env['ir.config_parameter'].sudo().set_param('web.base.url.freeze', 'True')
        except Exception:
            pass
        return result
