from openerp.osv import fields
from openerp.osv import osv
import openerp.addons.decimal_precision as dp
from openerp import workflow
from openerp.tools.translate import _
import time

class purchase_order(osv.osv):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            company = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])
            company_id = str(company.custom_customer_id)
            if vals['x_project_id']:
                project_id = str(vals['x_project_id'])
            else:
                project_id = "NPR"
            if vals['date_order']:
                date_prepared = str(time.strftime('%d%m%y',time.strptime(vals['date_order'],'%Y-%m-%d %H:%M:%S')))
            else:
                date_prepared = "NDATE"
            vals['name'] = company_id + "_" + project_id + "_" + date_prepared + "_" + self.pool.get('ir.sequence').get(cr, uid, 'purchase.order', context=context) or '/'
        context = dict(context or {}, mail_create_nolog=True)
        order =  super(purchase_order, self).create(cr, uid, vals, context=context)
        self.message_post(cr, uid, [order], body=_("RFQ created"), context=context)
        return order

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
                'discount': 0.0,
                'trans_value': 0.0
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            for line in order.order_line:
               val1 += line.price_subtotal
               for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            #res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax']

            dis = {}
            for line in self.browse(cr, uid, ids, context=context):
                dis[line.id] = line.discount

            trans = {}
            for line in self.browse(cr, uid, ids, context=context):
                trans[line.id] = line.tran_other

            t_dis_value = t_trans_value = 0.0

            t_dis_value = dis.values().__getitem__(0) #got the numerical value
            t_trans_value = trans.values().__getitem__(0) #got the numerical value

           # print "dis_value: ", t_dis_value
           # print "lin_value: ", t_trans_value

            res[order.id]['discount']=cur_obj.round(cr, uid, cur, t_dis_value)
            res[order.id]['line_value']=cur_obj.round(cr, uid, cur, t_trans_value)

            res[order.id]['amount_total'] = (res[order.id]['amount_untaxed'] - res[order.id]['discount']) + res[order.id]['amount_tax'] + res[order.id]['line_value']

           # print "Ress: ", res

        return res

    _columns = {
        'shipping_method' : fields.many2one('shipping.method', string='Shipping Method'),
        'shipping_terms' : fields.char(string='Shipping Terms'),
        'purpose_type' : fields.selection((('io', 'Internal/Office'), ('ep', 'External/Project')), string='Choose the Purpose'),
        'assignee' : fields.many2many("res.users", "assign_order_rel", "assignee_id", "order_id", string="Assignee"),
        'payment_mode' : fields.selection((('cash', 'Cash'), ('cheque', 'Cheque'), ('credit', 'Credit'), ('electronic', 'Electronic')), string="Payment Mode"),
        'shipping_time' : fields.selection((('1day', '1 Day'), ('2day', '2 Day'), ('1week', '1 Week'), ('1month', '1 Month')), string="Shipping Time"),
        'discount' : fields.float('Discount*'),
        'tran_other' : fields.float('Transport & Others'),
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total Payable',
            store=True, multi="sums", help="The total amount"),
        'req_by' : fields.char(string="Requested By"),
        'purpose' : fields.char(string="Purpose"),
        'x_project_id' : fields.char(string="Project ID", required=True),
        }

class shipping_method(osv.osv):
    _name='shipping.method'

    _columns = {
        'name' : fields.char(string="Name", required=True),
        'value' : fields.char(string="Value", required=True),
    }

    _sql_constraints = [('value', 'unique(value)', 'This value is used for another method.')] #('name', 'sql_definition', 'message')
    _sql_constraints = [('name', 'unique(name)', 'This name is used for another method.')] #('name', 'sql_definition', 'message')


#class purchase_custom_line(osv.osv):
#    _name = 'purchase.order.line'
#    _inherit = 'purchase.order.line'

#    _columns = {
#        'job_name' : fields.char(string='Project'),
#    }
