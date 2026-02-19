from odoo import http
from odoo.http import request

class CustomDashboard(http.Controller):

    @http.route('/custom_dashboard',type='http',auth='user',website=True)
    def custom_dashboard(self, **kwargs):
        return request.render('landing_page.dashboard_page')