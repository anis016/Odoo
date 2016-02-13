# -*- coding: utf-8 -*-
from openerp.osv import fields
from openerp.osv import osv
from openerp import SUPERUSER_ID, api
import time

class account_invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"

    _columns = {
        #'user_id' : fields.many2one('hr.employee', string="Sales Person"),
        'x_project_id' : fields.char(string="Project ID"),
    }

class invoice_line(osv.osv):
    _name = 'account.invoice.line'
    _inherit = 'account.invoice.line'

    _columns = {
        'x_delivery_date' : fields.datetime(string="Delivery Date")
    }

#        journal_names = {
#            'sale': _('Sales Journal'),
#            'purchase': _('Purchase Journal'),
#            'sale_refund': _('Sales Refund Journal'),
#            'purchase_refund': _('Purchase Refund Journal'),
#            'general': _('Miscellaneous Journal'),
#            'situation': _('Opening Entries Journal'),
#        }
#        journal_codes = {
#            'sale': _('SAJ'),
#            'purchase': _('EXJ'),
#            'sale_refund': _('SCNJ'),
#            'purchase_refund': _('ECNJ'),
#            'general': _('MISC'),
#            'situation': _('OPEJ'),
#        }
        
class account_move(osv.osv):
    _inherit = "account.move"
    
    def trim_and_return(self, string):
        length = len(string)
        for i in xrange(length-1, 0, -1):
            if string[i] == '_':
                break
        string = string[0:i]
        return string
    
    def post(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        invoice = context.get('invoice', False)
        valid_moves = self.validate(cr, uid, ids, context)
        
        if invoice.origin:
            source = self.trim_and_return(str(invoice.origin))
        else:        
            partner_id = invoice.partner_id.id
            project_id = str(invoice.x_project_id)
            company = self.pool.get('res.partner').browse(cr, uid, [partner_id])
            company_id = str(company.custom_customer_id)
            date_prepared = str(time.strftime('%d%m%y',time.strptime(invoice.date_invoice,'%Y-%m-%d')))

        if not valid_moves:
            raise osv.except_osv(_('Error!'), _('You cannot validate a non-balanced entry.\nMake sure you have configured payment terms properly.\nThe latest payment term line should be of the "Balance" type.'))
        obj_sequence = self.pool.get('ir.sequence')
        for move in self.browse(cr, uid, valid_moves, context=context):
            if move.name =='/':
                new_name = False
                journal = move.journal_id

                if invoice and invoice.internal_number:
                    new_name = invoice.internal_number
                else:
                    if journal.sequence_id:
                        c = {'fiscalyear_id': move.period_id.fiscalyear_id.id}
                        if invoice.origin:
                            new_name = source + "_" + obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                        else:
                            if project_id != 'False':
                                new_name = company_id + "_" + project_id + "_" + date_prepared + "_" + obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                            else:
                                new_name = company_id + "_" + date_prepared + "_" + obj_sequence.next_by_id(cr, uid, journal.sequence_id.id, c)
                    else:
                        raise osv.except_osv(_('Error!'), _('Please define a sequence on the journal.'))

                if new_name:
                    self.write(cr, uid, [move.id], {'name':new_name})

        cr.execute('UPDATE account_move '\
                   'SET state=%s '\
                   'WHERE id IN %s',
                   ('posted', tuple(valid_moves),))
        self.invalidate_cache(cr, uid, context=context)
        return True