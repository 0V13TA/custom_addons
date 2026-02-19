# -*- coding: utf-8 -*-
# from odoo import http


# class EnterpriseTheme(http.Controller):
#     @http.route('/enterprise_theme/enterprise_theme', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/enterprise_theme/enterprise_theme/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('enterprise_theme.listing', {
#             'root': '/enterprise_theme/enterprise_theme',
#             'objects': http.request.env['enterprise_theme.enterprise_theme'].search([]),
#         })

#     @http.route('/enterprise_theme/enterprise_theme/objects/<model("enterprise_theme.enterprise_theme"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('enterprise_theme.object', {
#             'object': obj
#         })

