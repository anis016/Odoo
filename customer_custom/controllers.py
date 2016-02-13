# -*- coding: utf-8 -*-
from openerp import http

# class CustomerCustom(http.Controller):
#     @http.route('/customer_custom/customer_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_custom/customer_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_custom.listing', {
#             'root': '/customer_custom/customer_custom',
#             'objects': http.request.env['customer_custom.customer_custom'].search([]),
#         })

#     @http.route('/customer_custom/customer_custom/objects/<model("customer_custom.customer_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_custom.object', {
#             'object': obj
#         })