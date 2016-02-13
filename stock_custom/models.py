# -*- coding: utf-8 -*-

from openerp.osv import fields
from openerp.osv import osv
import time
from openerp import SUPERUSER_ID, api

class stock_picking(osv.osv):
    _name = 'stock.picking'
    _inherit = 'stock.picking'
    
    def trim_and_return(self, string):
        length = len(string)
        for i in xrange(length-1, 0, -1):
            if string[i] == '_':
                break
        string = string[0:i]
        return string

    def create(self, cr, user, vals, context=None):
        context = context or {}
        if ('name' not in vals) or (vals.get('name') in ('/', False)):
            ptype_id = vals.get('picking_type_id', context.get('default_picking_type_id', False))
            sequence_id = self.pool.get('stock.picking.type').browse(cr, user, ptype_id, context=context).sequence_id.id
            #Custom added
            print "Vals:::", vals
            
            if vals.get('origin'):
                source = self.trim_and_return(str(vals['origin']))
                vals['name'] = source + "_" +  self.pool.get('ir.sequence').get_id(cr, user, sequence_id, 'id', context=context)
            else:
                company = self.pool.get('res.partner').browse(cr, user, vals['partner_id'])
                company_id = str(company.custom_customer_id)
                if vals.get('x_project_id_create'):
                    project_id = str(vals['x_project_id_create'])
                if vals.get('date'):
                    date_prepared = str(time.strftime('%d%m%y',time.strptime(vals['date'],'%Y-%m-%d %H:%M:%S')))
                else:
                    date_prepared = "No_Date"
                    
                if project_id != 'False':
                    vals['name'] = company_id + "_" + project_id + "_" + date_prepared + "_" +  self.pool.get('ir.sequence').get_id(cr, user, sequence_id, 'id', context=context)
                else:
                    vals['name'] = company_id + "_" + date_prepared + "_" +  self.pool.get('ir.sequence').get_id(cr, user, sequence_id, 'id', context=context)
            
        return super(stock_picking, self).create(cr, user, vals, context)
    
    _columns = {
        'x_submitted_by' : fields.many2one("res.users", string="Submitted By", required=True),
        'x_authorized_by' : fields.many2one("res.users", string="Authorized By", required=True),
        'x_project_id' : fields.related('sale_id','x_project_id', type="char", readonly=True, string="Project ID"),
        'x_project_id_create' : fields.char(string="Project ID"),
    }

class stock_move(osv.osv):
    _inherit = "stock.move"

    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        ret = super(stock_move, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)

        print "blah blah blah::::",move.date_expected

        if move.date_expected:
            ret['x_delivery_date'] = move.date_expected

        return ret