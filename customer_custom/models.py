# -*- coding: utf-8 -*-

from openerp import models, fields, api

class customer_custom(models.Model):
     _name = 'res.partner'
     _inherit = 'res.partner'

     custom_customer_id = fields.Char(string = "Customer ID", required=True)

     _sql_constraints = [('unique_customer_id', 'unique(custom_customer_id)', 'This customer id is in used for another customer.')] #('name', 'sql_definition', 'message')