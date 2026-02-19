# -*- coding: utf-8 -*-
# from odoo import http


# class HJubranPrd(http.Controller):
#     @http.route('/h_jubran_prd/h_jubran_prd', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/h_jubran_prd/h_jubran_prd/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('h_jubran_prd.listing', {
#             'root': '/h_jubran_prd/h_jubran_prd',
#             'objects': http.request.env['h_jubran_prd.h_jubran_prd'].search([]),
#         })

#     @http.route('/h_jubran_prd/h_jubran_prd/objects/<model("h_jubran_prd.h_jubran_prd"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('h_jubran_prd.object', {
#             'object': obj
#         })

