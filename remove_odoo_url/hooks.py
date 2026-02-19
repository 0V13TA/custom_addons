from odoo import api, SUPERUSER_ID

def post_init_hook(env):
    """Clean web.base.url and set default custom URL name"""
    base_url = env['ir.config_parameter'].sudo().get_param('web.base.url', '')
    if '/odoo' in base_url:
        new_base_url = base_url.replace('/odoo', '')
        env['ir.config_parameter'].sudo().set_param('web.base.url', new_base_url)
    
    # Set default custom URL name to 'aims' if not already set
    if not env['ir.config_parameter'].sudo().get_param('web.base.urlname'):
        env['ir.config_parameter'].sudo().set_param('web.base.urlname', 'aims')
