# -*- coding: utf-8 -*-
##############################################################################
#
#    Sales and Invoice Discount Management
#    Copyright (C) 2015 BrowseInfo(<http://www.browseinfo.in>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from docutils.nodes import field_name


class sale_order(osv.osv):
    _inherit = 'sale.order'

    def _amount_all_wrapper(self, cr, uid, ids, field_name, arg, context=None):
        """ Wrapper because of direct method passing as parameter for function fields """
        return self._amount_all(cr, uid, ids, field_name, arg, context=context)


    def _amount_line_tax(self, cr, uid, line, context=None):
        val = 0.0
        line_obj = self.pool['sale.order.line']
        price = line.price_unit
        #if line.discount_method == 'fix':
        #    price = price - line.discount
        #elif line.discount_method == 'per':
        #    price = price - (line.price_unit * ((line.discount or 0.0) / 100.0))
        #else:
        #    price = price
        qty = line.product_uom_qty or 0.0
        for c in self.pool['account.tax'].compute_all(
                cr, uid, line.tax_id, price, qty, line.product_id,
                line.order_id.partner_id)['taxes']:
            val += c.get('amount', 0.0)
        return val

    def _calculate_deposit(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        deposit = 0.0
        for self_obj in self.browse(cr, uid, ids, context=context):
            deposit = self_obj.deposit
            res[self_obj.id] = deposit
        return res

    def _calculate_discount(self, cr , uid, ids, field_name,  args, context={}):
        res = {}
        discount = 0.0
        for self_obj in self.browse(cr, uid, ids, context=context):
            if self_obj.discount_method == 'fix':
                discount = self_obj.discount_amount
                res[self_obj.id] = discount
            elif self_obj.discount_method == 'per':
                discount = self_obj.amount_untaxed * ((self_obj.discount_amount or 0.0) / 100.0)
                res[self_obj.id] = discount
            else:
                res[self_obj.id] = discount
            for line_obj in self_obj.order_line:
                if line_obj.discount_method == 'fix':
                    discount += line_obj.discount
                    res[self_obj.id] = discount
                elif line_obj.discount_method == 'per':
                    discount += line_obj.price_unit * ((line_obj.discount or 0.0) / 100.0)
                    res[self_obj.id] = discount
                else:
                    discount += 0.0
                    res[self_obj.id] = discount
        return res

    def _amount_all(self, cr, uid, ids, field_name, arg, context=None):
        cur_obj = self.pool.get('res.currency')
        res = {}
        order_discount = 0.0
        order_deposit  = 0.0
        for order in self.browse(cr, uid, ids, context=context):
            res[order.id] = {
                'amount_untaxed': 0.0,
                'amount_tax': 0.0,
                'amount_total': 0.0,
            }
            val = val1 = 0.0
            cur = order.pricelist_id.currency_id
            order_discount = order.discount_amt
            order_deposit  = order.deposit_amt
            for line in order.order_line:
                val1 += line.price_subtotal
                val += self._amount_line_tax(cr, uid, line, context=context)
            res[order.id]['amount_tax'] = cur_obj.round(cr, uid, cur, val)
            res[order.id]['amount_untaxed'] = cur_obj.round(cr, uid, cur, val1)
            res[order.id]['amount_total'] = res[order.id]['amount_untaxed'] + res[order.id]['amount_tax'] - order_discount - order_deposit
        return res

    def _get_order(self, cr, uid, ids, context=None):
        result = {}
        for line in self.pool.get('sale.order.line').browse(cr, uid, ids, context=context):
            result[line.order_id.id] = True
        return result.keys()
    
    def _calculate_total(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        total = 0.0
        for self_obj in self.browse(cr, uid, ids, context=context):
            selling_price = self_obj.amount_untaxed
            less_deposit = self_obj.deposit_amt
            transfer_fee = self_obj.tran_fee
            admin_and_doc_fee = self_obj.ad_doc_fee
            insurance = self_obj.insurance
            fin_service_charge = self_obj.fin_ser_charge
            fin_first_payment = self_obj.fin_1st_pay
            
            total = selling_price - less_deposit + transfer_fee + admin_and_doc_fee + insurance + fin_service_charge + fin_first_payment 
            
            res[self_obj.id] = total
        
        return res
    
    def _calculate_balance_payment(self, cr, uid, ids, field_name, args, context={}):
        res = {}
        balance_payment = 0.0
        for self_obj in self.browse(cr, uid, ids, context=context):
            total = self_obj.total
            less_finance = self_obj.less_finance
            
            balance_payment = total - less_finance 
            
            res[self_obj.id] = balance_payment
                    
        return res

    _columns = {
        'apply_discount_in_line': fields.boolean('Apply Discount in Line?', help='Help note'),
        'discount_method': fields.selection(
            [('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method'),
        'discount_amount': fields.float('Discount Amount'),
        'is_apply_on_discount_amount': fields.boolean(
            "Tax Apply After Discount"),
        'amount_untaxed': fields.function(
            _amount_all_wrapper,
            digits_compute=dp.get_precision('Account'),
            string='Untaxed Amount',
            store={'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                   'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10), },
            multi='sums', help="The amount without tax.", track_visibility='always'),
       'discount_amt': fields.function(
            _calculate_discount, string='- Discount', digits_compute=dp.get_precision('Account'),readonly=True,
        ),
        'amount_tax': fields.function(
            _amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Taxes',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The tax amount."),
        'amount_total': fields.function(_amount_all_wrapper, digits_compute=dp.get_precision('Account'), string='Total',
            store={
                'sale.order': (lambda self, cr, uid, ids, c={}: ids, ['order_line', 'discount_method', 'discount_amount', 'discount_amt', 'deposit', 'deposit_amt'], 10),
                'sale.order.line': (_get_order, ['price_unit', 'tax_id', 'discount', 'product_uom_qty'], 10),
            },
            multi='sums', help="The total amount."),

        # Customer end requirements
        'deposit': fields.float('Deposit'),
        'deposit_amt': fields.function(_calculate_deposit, readonly="True", digits_compute=dp.get_precision('Account'), string="- Deposit Amnt."),

        # New field added for the sales report agreement
        'handover_date': fields.datetime("Date of Handover", help="Which day it will be handovered ?"),
        'tran_fee': fields.float("Transfer Fee", default=0.0),
        'ad_doc_fee': fields.float("Admin & Document Fee", default=0.0),
        'insurance': fields.float("Insurance", default=0.0),
        'fin_ser_charge': fields.float("Finance Service Charge", default=0.0),
        'fin_1st_pay': fields.float("Finance 1st Payment", default=0.0),
        'total': fields.function(_calculate_total, readonly="True", digits_compute=dp.get_precision('Account'), string="Total"),
        'less_finance': fields.float("- Less Finance", default=0.0),
        'balance_paym': fields.function(_calculate_balance_payment, readonly="True", digits_compute=dp.get_precision('Account'), string="Balance Payment"),

        # Added new field for handling the vechicle
        'vehicles': fields.many2one('product.product', 'Vehicles')
    }

    def discount_set(self, cr, uid, ids, context=None):
        amount_total = self.browse(cr, uid, ids, context=context)[0].amount_untaxed
        amount_tax = self.browse(cr, uid, ids, context=context)[0].amount_tax
        disc_amt = self.browse(cr, uid, ids, context=context)[0].discount_amount
        deposit_amt = self.browse(cr, uid, ids, context=context)[0].deposit
        disc_methd = self.browse(cr, uid, ids, context=context)[0].discount_method
        apply_discount = self.browse(
            cr, uid, ids, context=context)[0].is_apply_on_discount_amount
        new_amt = 0.0
        new_amtt = 0.0
        if disc_amt:
            if disc_methd == 'fix':
                new_amt = amount_total - disc_amt - deposit_amt
                new_amtt = disc_amt
            if disc_methd == 'per':
                new_amtt = amount_total * disc_amt / 100
                new_amt = (amount_total * (1 - (disc_amt or 0.0) / 100.0)) - deposit_amt
            self.write(cr, uid, ids, {'discount_amt': new_amtt})
            sql = "update sale_order set amount_total=%s where id=%s"
            cr.execute(sql, (new_amt, ids[0]))
        return True

    def _prepare_invoice(self, cr, uid, order, lines, context=None):
        """Prepare the dict of values to create the new invoice for a
           sales order. This method may be overridden to implement custom
           invoice generation (making sure to call super() to establish
           a clean extension chain).

           :param browse_record order: sale.order record to invoice
           :param list(int) line: list of invoice line IDs that must be
                                  attached to the invoice
           :return: dict of value to create() the invoice
        """
        if context is None:
            context = {}
        journal_ids = self.pool.get('account.journal').search(
            cr, uid, [('type', '=', 'sale'), ('company_id', '=', order.company_id.id)],
            limit=1)
        if not journal_ids:
            raise osv.except_osv(
                _('Error!'),
                _('Please define sales journal for this company: "%s" (id:%d).') % (order.company_id.name, order.company_id.id))
        invoice_vals = {
            'name': order.client_order_ref or '',
            'origin': order.name,
            'type': 'out_invoice',
            'reference': order.client_order_ref or order.name,
            'account_id': order.partner_id.property_account_receivable.id,
            'partner_id': order.partner_invoice_id.id,
            'journal_id': journal_ids[0],
            'invoice_line': [(6, 0, lines)],
            'currency_id': order.pricelist_id.currency_id.id,
            'comment': order.note,
            'payment_term': order.payment_term and order.payment_term.id or False,
            'fiscal_position': order.fiscal_position.id or order.partner_id.property_account_position.id,
            'date_invoice': context.get('date_invoice', False),
            'company_id': order.company_id.id,
            'discount_method': order.discount_method,
            'discount_amount': order.discount_amount,
            'deposit': order.deposit, # Added the deposit amount
            'user_id': order.user_id and order.user_id.id or False
        }

        # Care for deprecated _inv_get() hook - FIXME: to be removed after 6.1
        invoice_vals.update(self._inv_get(cr, uid, order, context=context))
        return invoice_vals

sale_order()


class sale_order_line(osv.osv):
    _inherit = 'sale.order.line'
    def _amount_line(self, cr, uid, ids, field_name, arg, context=None):
        tax_obj = self.pool.get('account.tax')
        cur_obj = self.pool.get('res.currency')
        res = {}
        if context is None:
            context = {}
        for line in self.browse(cr, uid, ids, context=context):
            price = line.price_unit
            qty = line.product_uom_qty or 0.0
            taxes = tax_obj.compute_all(
                cr, uid, line.tax_id, price, qty, line.product_id, line.order_id.partner_id)
            cur = line.order_id.pricelist_id.currency_id
          #  res = line.order_id._amount_all
            res[line.id] = cur_obj.round(cr, uid, cur, taxes['total'])
        return res

    _columns = {
        'is_apply_on_discount_amount': fields.boolean(
            "Tax Apply After Discount"),
        'discount_method': fields.selection(
            [('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method'),
        'price_subtotal': fields.function(_amount_line, string='Subtotal',digits_compute=dp.get_precision('Account')),
        
        # Customer requirements
        # 'deposit' : fields.float('Deposit'),
        # 'transfer_fee':fields.float('Transfer fee'),
        # 'ad_doc_fee':fields.float('Admin & Document fee'),
        # 'insurance':fields.float('Insurance'),
        # 'fin_charge':fields.float('Finance Service Charge'),
        # 'fin_first_payment':fields.float('Finance 1st Payment'),
        # 'lease_fin':fields.float('Finance'),
        }

    def _prepare_order_line_invoice_line(self, cr, uid, line, account_id=False,
                                         context=None):
        res = super(sale_order_line,
                    self)._prepare_order_line_invoice_line(
                        cr, uid, line=line, account_id=account_id,
                        context=context)
        res.update({'discount_method': line.discount_method,
                    })
        return res

sale_order_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:s
