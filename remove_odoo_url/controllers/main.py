from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.home import Home

class RemoveOdooUrlHome(Home):
    
    def _get_custom_url_name(self):
        """Get custom URL name from system parameter, default to 'enterpriseone'"""
        try:
            return request.env['ir.config_parameter'].sudo().get_param('web.base.urlname', 'enterpriseone')
        except:
            return 'enterpriseone'
    
    @http.route('/', type='http', auth="none")
    def index(self, s_action=None, db=None, **kw):
        """Redirect root to custom URL (enterpriseone by default)"""
        custom_name = self._get_custom_url_name()
        return request.redirect_query(f'/{custom_name}', query=request.params)
    
    # Serve web client at /enterpriseone (hardcoded default)
    @http.route(['/enterpriseone', '/enterpriseone/<path:subpath>'], type='http', auth="none")
    def web_client_enterpriseone(self, s_action=None, **kw):
        """Serve web client at /enterpriseone (default custom name)"""
        return super().web_client(s_action=s_action, **kw)
    
    # Dynamic route: Serve web client at custom configured URL name
    @http.route(['/<string:custom_name>', '/<string:custom_name>/<path:subpath>'], type='http', auth="none")
    def web_client_custom_dynamic(self, custom_name=None, subpath=None, s_action=None, **kw):
        """Serve web client at dynamically configured custom URL"""
        configured_name = self._get_custom_url_name()
        
        # Only serve if this matches our configured custom name
        if custom_name == configured_name:
            return super().web_client(s_action=s_action, **kw)
        
        # Otherwise, let it fall through (will likely 404 or hit another controller)
        # Don't handle it - this prevents us from catching everything
        pass
    
    # Override parent /web and /odoo routes by redefining web_client with redirects
    @http.route(['/web', '/web/<path:subpath>', '/odoo', '/odoo/<path:subpath>'], type='http', auth="none")  
    def web_client(self, s_action=None, **kw):
        """Override parent routes and redirect to custom URL"""
        custom_name = self._get_custom_url_name()
        path = request.httprequest.path
        
        # Exception for special Odoo paths
        if path.startswith('/web/login') or path.startswith('/web/content') or path.startswith('/web/static') or path.startswith('/web/assets') or path.startswith('/web/image'):
             # Call parent for these special paths
             return super().web_client(s_action=s_action, **kw)
        
        # Extract subpath if present
        subpath = None
        if path.startswith('/web/'):
            subpath = path[5:]  # Remove /web/
        elif path.startswith('/odoo/'):
            subpath = path[6:]  # Remove /odoo/
        
        # Build redirect target
        target = f'/{custom_name}'
        if subpath:
            target += f'/{subpath}'
        
        query = request.httprequest.query_string.decode('utf-8')
        if query:
            target += f'?{query}'
            
        return request.redirect(target, 301)
