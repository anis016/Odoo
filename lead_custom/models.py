# -*- coding: utf-8 -*-

import openerp
from openerp.osv import fields, osv

class crm_lead(osv.osv):
    _name = 'crm.lead'
    _inherit = 'crm.lead'

    _columns = {
        'x_project_id' : fields.char(string = "Project ID", required=True),
        #'user_id' : fields.many2one('hr.employee', string="Sales Person"),
    }
