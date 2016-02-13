# -*- coding: utf-8 -*-

from openerp.osv import fields, osv
import time
import base64
import re
import openerp
from openerp.tools.translate import _

class sale_order(osv.osv):
    _name = 'sale.order'
    _inherit = ['sale.order', 'mail.thread']

    def _action_generate_attachment(self, cr, uid, res_id, context=None):
        ''' This generates the report and save into the attachment. '''

        attachment_obj = self.pool.get('ir.attachment')
        for numbers in self.browse(cr, uid, res_id, context=context):
            record = numbers

        ir_actions_report = self.pool.get('ir.actions.report.xml')
        matching_reports = ir_actions_report.search(cr, uid, [('model','=',self._name),
                                                              ('report_name','=','sale_report.report_naz_sales')])
        print "matching_reports:::: ", matching_reports
        if matching_reports:
            report = ir_actions_report.browse(cr, uid, matching_reports[0])
            result, format = openerp.report.render_report(cr, uid, [record.id], report.report_name, {'model': self._name}, context=context)
            eval_context = {'time': time, 'object': record}
            if not report.attachment or not eval(report.attachment, eval_context):
                # no auto-saving of report as attachment, need to do it manually
                result = base64.b64encode(result)
                file_name = record.name_get()[0][1]
                file_name = re.sub(r'[^a-zA-Z0-9_-]', '_', file_name)
                file_name += ".pdf"
                attachment_id = attachment_obj.create(cr, uid,
                    {
                        'name': file_name,
                        'datas': result,
                        'datas_fname': file_name,
                        'res_model': self._name,
                        'res_id': record.id,
                        'type': 'binary'
                    }, context=context)
        return attachment_id

    def create(self, cr, uid, vals, context=None):
        if context is None:
            context = {}
        if vals.get('name', '/') == '/':
            company = self.pool.get('res.partner').browse(cr, uid, vals['partner_id'])
            company_id = str(company.custom_customer_id)
            if vals['x_project_id']:
                project_id = str(vals['x_project_id'])
            else:
                project_id = "NPR"
            date_prepared = str(time.strftime('%d%m%y',time.strptime(vals['date_order'],'%Y-%m-%d %H:%M:%S')))
            vals['name'] = company_id + "_" + project_id + "_" + date_prepared + "_" + self.pool.get('ir.sequence').get(cr, uid, 'sale.order', context=context) or '/'
        if vals.get('partner_id') and any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id', 'fiscal_position']):
            defaults = self.onchange_partner_id(cr, uid, [], vals['partner_id'], context=context)['value']
            if not vals.get('fiscal_position') and vals.get('partner_shipping_id'):
                delivery_onchange = self.onchange_delivery_id(cr, uid, [], vals.get('company_id'), None, vals['partner_id'], vals.get('partner_shipping_id'), context=context)
                defaults.update(delivery_onchange['value'])
            vals = dict(defaults, **vals)
        ctx = dict(context or {}, mail_create_nolog=True)
        new_id = super(sale_order, self).create(cr, uid, vals, context=ctx)
        self.message_post(cr, uid, [new_id], body=_("Quotation created"), context=ctx)
        return new_id
    
    def _make_invoice(self, cr, uid, order, lines, context=None):
        inv_id = super(sale_order, self)._make_invoice(cr, uid, order, lines, context)
        inv_obj = self.pool.get('account.invoice')
        if order.partner_shipping_id:
            inv_obj.write(cr, uid, [inv_id], {'x_project_id': order.x_project_id}, context=context)
        return inv_id

    def append_to_message_communication(self, cr, uid, vals, context=None):

        attach = []
        attach.append(self._action_generate_attachment(cr, uid, vals, context=context))
        print attach
        
        sale_obj = self.pool.get('sale.order').browse(cr, uid, vals[0], context=context)
        body = ""
        if sale_obj.state == 'draft':
            body = "Sales Draft Quotation saved."
        else:
            body = "Sales Order saved."
            
        self.message_post(cr, uid, vals, body=body, attachment_ids=attach,context=context)
        return attach

    _columns = {
       # 'user_id' : fields.many2one('hr.employee', string="Sales Person"),
        'x_project_id' : fields.char(string="Project ID"),
    }

sale_order()
