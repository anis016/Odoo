# -*- coding: utf-8 -*-
from openerp import http

# class SalesCustom(http.Controller):
#     @http.route('/sale_crm_custom/sale_crm_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_crm_custom/sale_crm_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_crm_custom.listing', {
#             'root': '/sale_crm_custom/sale_crm_custom',
#             'objects': http.request.env['sale_crm_custom.sale_crm_custom'].search([]),
#         })

#     @http.route('/sale_crm_custom/sale_crm_custom/objects/<model("sale_crm_custom.sale_crm_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_crm_custom.object', {
#             'object': obj
#         })