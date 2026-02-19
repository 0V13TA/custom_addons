# -*- coding: utf-8 -*-
# from odoo import http


# class Practice(http.Controller):
#     @http.route('/practice/practice', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/practice/practice/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('practice.listing', {
#             'root': '/practice/practice',
#             'objects': http.request.env['practice.practice'].search([]),
#         })

#     @http.route('/practice/practice/objects/<model("practice.practice"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('practice.object', {
#             'object': obj
#         })

