from openerp.osv import fields, orm
from openerp.tools.translate import _
from openerp.tools import ustr
from openerp import SUPERUSER_ID, api

class mail_message(orm.Model):
    _inherit = ['mail.message']

    def compute_partner(self, cr, uid, active_model='res.partner', model='mail.message', res_id=1, context=None):
        if context is None:
            context = {}
        target_ids = []
        current_obj = self.pool.get(model)
        cr.execute("SELECT name FROM ir_model_fields WHERE relation='" + active_model + "' and model = '" + model + "' and ttype not in ('many2many', 'one2many');")
        for name in cr.fetchall():
            current_data = current_obj.read(cr, uid, res_id, [str(name[0])],context=context)
            if current_data.get(str(name[0])):
                var = current_data.get(str(name[0]))
                if var:
                    target_ids.append(var[0])

        cr.execute("select name, model from ir_model_fields where relation='" + model + "' and ttype in ('many2many') and model = '" + active_model + "';")
        for field, model in cr.fetchall():
            field_data = self.pool.get(model) and self.pool.get(model)._columns.get(field, False) \
                            and (isinstance(self.pool.get(model)._columns[field], fields.many2many) \
                            or isinstance(self.pool.get(model)._columns[field], fields.function) \
                            and self.pool.get(model)._columns[field].store) \
                            and self.pool.get(model)._columns[field] \
                            or False
            if field_data:
                model_m2m, rel1, rel2 = field_data._sql_names(self.pool.get(model))
                requete = "SELECT "+rel1+" FROM "+ model_m2m+" WHERE "+ rel2+" ="+str(res_id)+";"
                cr.execute(requete)
                sec_target_ids = cr.fetchall()
                for sec_target_id in sec_target_ids:
                    target_ids.append(sec_target_id[0])
        return target_ids

    def _get_object_name(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        model_obj = self.pool.get('ir.model')
        for message in self.browse(cr, uid, ids, context=context):
            if message.model == 'sale.order':
                res_id = message.res_id
                order_obj = self.pool.get('sale.order')
                for order_id in order_obj.browse(cr, uid, res_id, context=context):
                        state_name = order_id.state
                        string_name = ""
                        if state_name:
                            if state_name == 'draft':
                                string_name = 'Sales Draft Quotation'
                            elif state_name == 'sent':
                                string_name = 'Sales Quotation Sent'
                            elif state_name == 'cancel':
                                string_name = 'Sales Cancelled'
                            elif state_name == 'waiting_date':
                                string_name = 'Sales Waiting Schedule'
                            elif state_name == 'progress':
                                string_name = 'Sales Order'
                            elif state_name == 'manual':
                                string_name = 'Sales to Invoice'
                            elif state_name == 'shipping_except':
                                string_name = 'Sales Shipping Exception'
                            elif state_name == 'invoice_except':
                                string_name = 'Sales Invoice Exception'
                            elif state_name == 'done':
                                string_name = 'Sales Done'

                        result[message.id] = string_name
            else:
                model_ids = model_obj.search(cr, uid, [('model','=',message.model)], limit=1)
                if model_ids:
                    model_name = model_obj.browse(cr, uid, model_ids[0], context=context).name
                    result[message.id] = model_name
        return result

    def _get_body_txt(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        for message in self.browse(cr, uid, ids, context=context):
            if message.res_id:
                record_data = self.pool.get(message.model).browse(cr, uid, message.res_id, context=context)
                if message.model == 'crm.phonecall':
                    body_txt = record_data.name
                elif message.model == 'crm.meeting' or message.model == 'crm.lead':
                    body_txt = record_data.description
                else:
                    body_txt = record_data.name
                result[message.id] = body_txt
        return result

    # Modified the default function and changed to download from the attachment directly
    def _download_attachment(self, cr, uid, id_message, attachment_id, context=None):
        """ Return the content of linked attachments. """
        # this will fail if you cannot read the message
        message_values = self.read(cr, uid, [id_message], ['attachment_ids'], context=context)[0]
        if attachment_id in message_values['attachment_ids']:
            attachment = self.pool.get('ir.attachment').browse(cr, SUPERUSER_ID, attachment_id, context=context)
            if attachment.datas and attachment.datas_fname:
                return {
                        # FIX for direct attachment download
                        'type' : 'ir.actions.act_url',
                        'url': '/web/binary/saveas?model=ir.attachment&field=datas&filename_field=name&id=%s' %( attachment_id, ),
                        'target': 'self',
                }
        return False

    def get_attachment(self, cr, uid, vals, context=None):

        id_message = -1
        attachment_id = -1

        for numbers in self.browse(cr, uid, vals, context=context):
            record = numbers

        id_message = vals[0]
        attachment_id = record.attachment_ids.id

        return self._download_attachment(cr, uid, id_message, attachment_id, context=context)

    _columns = {
        'partner_ids': fields.many2many('res.partner', 'message_partner_rel', 'message_id', 'partner_id', 'Partners'),
        'object_name': fields.function(_get_object_name, type='char', string='Object Name', size=64, store=True),
        'body_txt': fields.function(_get_body_txt, type='text', string='Content', store=True),
        'project_id': fields.char(string='Project ID'),
    }

    _order= 'date desc'

    def create(self, cr, uid, vals, context=None):
        if not vals.get('partner_ids'):
            target_ids = []
            if vals.get('res_id') and vals.get('model'):
                target_ids = self.compute_partner(cr, uid, active_model='res.partner', model=vals.get('model'), res_id=vals.get('res_id'), context=context)
                target_ids = list(set(target_ids))
            vals.update({'partner_ids': [(6, 0, target_ids)],})
        return super(mail_message, self).create(cr, uid, vals, context=context)

class res_partner(orm.Model):
    _inherit = 'res.partner'

    def _get_message(self, cr, uid, ids, field_name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        message_obj = self.pool.get('mail.message')
        for partner in self.browse(cr, uid, ids, context=context):
            target_ids = message_obj.search(cr, uid, [
                    '|',('partner_ids', 'in', partner.id),
                    '&',('model', '=', 'res.partner'),('res_id','=',partner.id)
                ], order='date desc', context=context)
            result[partner.id] = target_ids

        for id in target_ids:
            for line in message_obj.browse(cr, uid, id, context=context):
                res_id = line.res_id
                model = line.model

                if model == 'crm.lead':
                    crm_lead_obj = self.pool.get('crm.lead')
                    for lead_id in crm_lead_obj.browse(cr, uid, res_id, context=context):
                        project_id = lead_id.x_project_id

                        if project_id:
                            message_obj.write(cr, uid, [id], {'project_id': project_id}, context=context)

                if model == 'sale.order':
                    order_obj = self.pool.get('sale.order')
                    for lead_id in order_obj.browse(cr, uid, res_id, context=context):
                        project_id = lead_id.x_project_id

                        if project_id:
                            message_obj.write(cr, uid, [id], {'project_id': project_id}, context=context)

                if model == 'account.invoice':
                    invoice_obj = self.pool.get('account.invoice')
                    for lead_id in invoice_obj.browse(cr, uid, res_id, context=context):
                        project_id = lead_id.x_project_id

                        if project_id:
                            message_obj.write(cr, uid, [id], {'project_id': project_id}, context=context)

                if model == 'stock.picking':
                    stock_obj = self.pool.get('stock.picking')
                    for lead_id in stock_obj.browse(cr, uid, res_id, context=context):
                        project_id = lead_id.x_project_id

                        if project_id:
                            message_obj.write(cr, uid, [id], {'project_id': project_id}, context=context)

        return result

    _columns = {
        # History follow-up #
        'history_ids': fields.function(_get_message, type='many2many', relation="mail.message", string="Related Messages"),
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
