# -*- coding: utf-8 -*-
# from odoo import http


# class Rebrands(http.Controller):
#     @http.route('/rebrands/rebrands', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/rebrands/rebrands/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('rebrands.listing', {
#             'root': '/rebrands/rebrands',
#             'objects': http.request.env['rebrands.rebrands'].search([]),
#         })

#     @http.route('/rebrands/rebrands/objects/<model("rebrands.rebrands"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('rebrands.object', {
#             'object': obj
#         })

