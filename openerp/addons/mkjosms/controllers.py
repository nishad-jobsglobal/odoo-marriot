# -*- coding: utf-8 -*-
from openerp import http

# class Mkjosms(http.Controller):
#     @http.route('/mkjosms/mkjosms/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mkjosms/mkjosms/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mkjosms.listing', {
#             'root': '/mkjosms/mkjosms',
#             'objects': http.request.env['mkjosms.mkjosms'].search([]),
#         })

#     @http.route('/mkjosms/mkjosms/objects/<model("mkjosms.mkjosms"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mkjosms.object', {
#             'object': obj
#         })