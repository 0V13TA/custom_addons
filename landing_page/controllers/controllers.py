# -*- coding: utf-8 -*-
# from odoo import http


# class LandingPage(http.Controller):
#     @http.route('/landing_page/landing_page', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/landing_page/landing_page/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('landing_page.listing', {
#             'root': '/landing_page/landing_page',
#             'objects': http.request.env['landing_page.landing_page'].search([]),
#         })

#     @http.route('/landing_page/landing_page/objects/<model("landing_page.landing_page"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('landing_page.object', {
#             'object': obj
#         })

