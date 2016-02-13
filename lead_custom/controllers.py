# -*- coding: utf-8 -*-
from openerp import http

# class LeadCustom(http.Controller):
#     @http.route('/lead_custom/lead_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lead_custom/lead_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lead_custom.listing', {
#             'root': '/lead_custom/lead_custom',
#             'objects': http.request.env['lead_custom.lead_custom'].search([]),
#         })

#     @http.route('/lead_custom/lead_custom/objects/<model("lead_custom.lead_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lead_custom.object', {
#             'object': obj
#         })