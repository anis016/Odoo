# -*- coding: utf-8 -*-
from openerp import http

# class MailThread(http.Controller):
#     @http.route('/mail_thread/mail_thread/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mail_thread/mail_thread/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mail_thread.listing', {
#             'root': '/mail_thread/mail_thread',
#             'objects': http.request.env['mail_thread.mail_thread'].search([]),
#         })

#     @http.route('/mail_thread/mail_thread/objects/<model("mail_thread.mail_thread"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mail_thread.object', {
#             'object': obj
#         })