from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

class purchase_order(osv.osv):
    _inherit="purchase.order"
    
    def deposit_set(self, cr, uid, ids, context=None):
        amount_total = self.browse(cr, uid, ids, context=context)[0].amount_untaxed
        amount_tax = self.browse(cr, uid, ids, context=context)[0].amount_tax
        deposit_amt = self.browse(cr, uid, ids, context=context)[0].deposit
        new_amt = 0.0
        if deposit_amt:
            new_amt = amount_total - deposit_amt
            self.write(cr, uid, ids, {'deposit_amt': new_amt})
            sql = "update purchase_order set amount_total=%s where id=%s"
            cr.execute(sql, (new_amt, ids[0]))
        return True
    
    def _calculate_deposit(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        deposit = 0.0
        for self_obj in self.browse(cr, uid, ids, context=context):
            deposit = self_obj.deposit
            res[self_obj.id] = deposit
        return res

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        cur_obj=self.pool.get('res.currency')
        order_deposit  = 0.0
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            order_deposit = order.deposit_amt
            for line in order.order_line:
               val1 += line.price_subtotal
               for c in self.pool.get('account.tax').compute_all(cr, uid, line.taxes_id, line.price_unit, line.product_qty, line.product_id, order.partner_id)['taxes']:
                    val += c.get('amount', 0.0)
            res[order.id]['amount_tax']=cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed']=cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total']=res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] - order_deposit
            
        return res

    def _prepare_invoice(self, cr, uid, order, line_ids, context=None):
        """Prepare the dict of values to create the new invoice for a
           purchase order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: purchase.order record to invoice
           :param list(int) line_ids: list of invoice line IDs that must be
                                      attached to the invoice
           :return: dict of value to create() the invoice
        """
        journal_ids = self.pool['account.journal'].search(
                            cr, uid, [('type', '=', 'purchase'),
                                      ('company_id', '=', order.company_id.id)],
                            limit=1)
        if not journal_ids:
            raise osv.except_osv(
                _('Error!'),
                _('Define purchase journal for this company: "%s" (id:%d).') % \
                    (order.company_id.name, order.company_id.id))
        return {
            'name': order.partner_ref or order.name,
            'reference': order.partner_ref or order.name,
            'account_id': order.partner_id.property_account_payable.id,
            'type': 'in_invoice',
            'partner_id': order.partner_id.id,
            'currency_id': order.currency_id.id,
            'journal_id': len(journal_ids) and journal_ids[0] or False,
            'invoice_line': [(6, 0, line_ids)],
            'origin': order.name,
            'fiscal_position': order.fiscal_position.id or False,
            'payment_term': order.payment_term_id.id or False,
            'company_id': order.company_id.id,
            'deposit': order.deposit, # Added the deposit amount
        }

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('purchase.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()

    _columns = {
        'amount_total': fields.function(_amount_all, digits_compute=dp.get_precision('Account'), string='Total',
            store=True, multi="sums", help="The total amount"),

        # Customer end requirements
        'deposit': fields.float('Deposit'),
        'deposit_amt': fields.function(_calculate_deposit, readonly="True", digits_compute=dp.get_precision('Account'), string="- Deposit Amnt.")
    }