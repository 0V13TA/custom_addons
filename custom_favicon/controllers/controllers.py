# -*- coding: utf-8 -*-
# from odoo import http


# class CustomFavicon(http.Controller):
#     @http.route('/custom_favicon/custom_favicon', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_favicon/custom_favicon/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_favicon.listing', {
#             'root': '/custom_favicon/custom_favicon',
#             'objects': http.request.env['custom_favicon.custom_favicon'].search([]),
#         })

#     @http.route('/custom_favicon/custom_favicon/objects/<model("custom_favicon.custom_favicon"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_favicon.object', {
#             'object': obj
#         })

