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

from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    @api.one
    def _calculate_discount(self):
        discount = 0.0
        if self.discount_method == 'fix':
            discount = self.discount_amount
        elif self.discount_method == 'per':
            discount = self.amount_untaxed * ((self.discount_amount or 0.0) / 100.0)
        else:
            discount += 0.0
        for line_obj in self.invoice_line:
            if line_obj.discount_method == 'fix':
                discount += line_obj.discount
            elif line_obj.discount_method == 'per':
                discount += line_obj.price_unit * ((line_obj.discount or 0.0) / 100.0)
            else:
                discount += 0.0
        self.discount_amt = discount
        
    @api.one
    def _calculate_deposit(self):
        
        deposit = 0.0
        if self.deposit:
            deposit = self.deposit
             
        self.deposit_amt = deposit

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'discount_amt', 'discount_method', 'discount_amount', 'deposit', 'deposit_amt')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)
        self.amount_total = self.amount_untaxed + self.amount_tax - self.discount_amt - self.deposit_amt
        self.residual = self.amount_untaxed + self.amount_tax - self.discount_amt - self.deposit_amt
        
    discount_method = fields.Selection(
        [('fix', 'Fixed'), ('per', 'Percentage')],
        'Discount Method')
    discount_amount = fields.Float('Discount Amount')
    discount_amt = fields.Float(
        string='- Discount', readonly=True, compute='_calculate_discount')
    amount_untaxed = fields.Float(
        string='Subtotal', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount',
        track_visibility='always')
    amount_tax = fields.Float(
        string='Tax', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount')
    amount_total = fields.Float(
        string='Total', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount')
    residual = fields.Float(
        string='Balance', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_amount')
    
    # for the deposit calculation
    deposit = fields.Float('Deposit')
    deposit_amt = fields.Float(compute='_calculate_deposit', readonly="True", string="- Deposit Amnt.")
    
    # for the vehicle informations
    vehicles = fields.Many2one('product.product', 'Vehicles')

    @api.one
    def discount_set(self):
        amount_total = self.amount_untaxed
        disc_amt = self.discount_amount
        disc_methd = self.discount_method
        new_amt = 0.0
        new_amtt = 0.0
        if disc_amt:
            if disc_methd == 'fix':
                new_amt = amount_total - disc_amt
                new_amtt = disc_amt
            if disc_methd == 'per':
                new_amtt = amount_total * disc_amt / 100
                new_amt = amount_total * (1 - (disc_amt or 0.0) / 100.0)
            self.write({'discount_amt': new_amtt})
            sql = "update account_invoice set amount_total=%s where id=%s"
            self._cr.execute(sql, (new_amt, self.id))
        return True

account_invoice()


class account_invoice_line(models.Model):
    _inherit = 'account.invoice.line'
    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_id', 'quantity',
                 'product_id', 'invoice_id.partner_id',
                 'invoice_id.currency_id')
    def _compute_price(self):
        price = self.price_unit
        taxes = self.invoice_line_tax_id.compute_all(
            price, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)


    discount_method = fields.Selection(
            [('fix', 'Fixed'), ('per', 'Percentage')], 'Discount Method')
    price_subtotal = fields.Float(
        string='Amount', digits=dp.get_precision('Account'),
        store=True, readonly=True, compute='_compute_price')

account_invoice_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
