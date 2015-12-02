# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Serpent Consulting Services Pvt. Ltd. (<http://www.serpentcs.com>)
#    Copyright (C) 2004 OpenERP SA (<http://www.openerp.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import except_orm, Warning
from dateutil.relativedelta import relativedelta
from openerp import models,fields,api,_
from openerp import netsvc
from calendar import isleap
from datetime import date, timedelta, datetime

class insurance_folio(models.Model):

    @api.multi
    def copy(self,default=None):
        '''
        @param self : object pointer
        @param default : dict of default values to be set
        '''
        return self.env['sale.order'].copy(default=default)

    @api.multi
    def _invoiced(self, name, arg):
        '''
        @param self : object pointer
        @param name: Names of fields.
        @param arg: User defined arguments
        '''
        return self.env['sale.order']._invoiced(name, arg)

    @api.multi
    def _invoiced_search(self ,obj, name, args):
        '''
        @param self : object pointer
        @param name: Names of fields.
        @param arg: User defined arguments
        '''
        return self.env['sale.order']._invoiced_search(obj, name, args)

    _name = 'insurance.folio'
    _description = 'insurance folio new'
    _rec_name = 'order_id'
    _order = 'id desc'

    order_id = fields.Many2one('sale.order','Order',  delegate=True, required=True, ondelete='cascade')
    insurance_lines = fields.One2many('insurance.folio.line','folio_id', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Vehicles Booking detail.")
    #service_lines = fields.One2many('insurance.folio.line','folio_id', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Hotel services detail provide to customer and it will include in main Invoice.")
    #hotel_policy = fields.Selection([('prepaid', 'On Booking'), ('manual', 'On Start Date'), ('picking', 'On Return Day')], 'Rent Policy',default='prepaid', help="Rental policy ")
    duration = fields.Float('Duration in Days', help="Number of days which will automatically count from the Start Date and End date. ")

    policy_start = fields.Date('Policy Start Date', required=True, readonly=False, states={'draft':[('readonly', False)]},default=lambda *a: date.today())
    policy_end = fields.Date('Policy End Date', readonly=False, store=True, compute = '_get_end_date')
    name = fields.Char('Confirmation Number', size=24,default=lambda obj: obj.env['ir.sequence'].get('insurance.folio'),readonly=True)

    date_select = fields.Selection([('week', 'Week'), ('day', 'Day'), ('month', 'Month'), ('year', 'Year')], "Date Range Selection", default="day")
    date_length = fields.Integer("Date Length", default=0)
    insurance_company = fields.Many2one('insurance.confirm_details')
    # Insurance Company information
    ins_company = fields.Char(string='Insurance Company', related='insurance_company.company_id.company_name')
    ins_amount = fields.Float(string='Insurance Amount', related='insurance_company.amount')
    
    ins_company_new = fields.Char(string='Insurance Company New')
    ins_amount_new = fields.Float(string='Insurance Amount New')
    
    #Comission field
    commision = fields.Char(string='Commision')


    @api.depends('policy_start', 'date_select', 'date_length')
    def _get_end_date(self):

        start_date = datetime.strptime(self.policy_start, "%Y-%m-%d")

        if self.date_select == "month":
            n = int(self.date_length)
            calculate_day = 0
            days_per_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            get_month = start_date.month
            get_year = start_date.year
            for i in range(n):
                if isleap(get_year) and get_month == 2:
                    calculate_day += 29
                else:
                    calculate_day += days_per_month[get_month - 1]

                get_month += 1
                if get_month > 12:
                    get_month = 1
                    get_year += 1

        elif self.date_select == "week":
            n = int(self.date_length)
            calculate_day = 7 * n

        elif self.date_select == "day":
            calculate_day = int(self.date_length)

        elif self.date_select == "year":
            n = int(self.date_length)
            if isleap(n):
                calculate_day = 366 * n
            else:
                calculate_day = 365 * n

        self.policy_end = start_date + timedelta(days=calculate_day)

    @api.constrains('policy_start','policy_end')
    def check_dates(self):
        '''
        This method is used to validate the policy_start and policy_end.
        -------------------------------------------------------------------
        @param self : object pointer
        @return : raise warning depending on the validation
        '''
        if self.policy_start >= self.policy_end:
                raise except_orm(_('Warning'),_('Policy Start Date Should be less than the Policy End Date!'))

    @api.constrains('insurance_lines')
    def check_folio_room_line(self):
        '''
        This method is used to validate the insurance_lines.
        ------------------------------------------------
        @param self : object pointer
        @return : raise warning depending on the validation
        '''
        folio_rooms = []
        for room in self[0].insurance_lines:
            if room.product_id.id in folio_rooms:
                raise except_orm(_('Warning'),_('You Cannot Take Same Service Twice'))
            folio_rooms.append(room.product_id.id)

    @api.onchange('policy_end','policy_start')
    def onchange_dates(self):
        '''
        This mathod gives the duration between check in checkout if customer will leave only for some
        hour it would be considers as a whole day. If customer will checkin checkout for more or equal
        hours , which configured in company as additional hours than it would be consider as full days
        ---------------------------------------------------------------------------------------------
        @param self : object pointer
        @return : Duration and policy_end
        '''
        myduration = 0
        if self.policy_start and self.policy_end:
            dur = datetime.strptime(self.policy_end, "%Y-%m-%d") - datetime.strptime(self.policy_start, "%Y-%m-%d")
            myduration = dur.days
        self.duration = myduration

    @api.model
    def create(self, vals,check=True):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for hotel folio.
        """
        tmp_insurance_lines = vals.get('insurance_lines', [])
        #vals['order_policy'] = vals.get('hotel_policy', 'prepaid')
        #if not 'service_lines' and 'folio_id' in vals:
        if 'folio_id' in vals:
                vals.update({'insurance_lines':[]})
                folio_id = super(insurance_folio, self).create(vals)
                for line in (tmp_insurance_lines):
                    line[2].update({'folio_id':folio_id})
                vals.update({'insurance_lines':tmp_insurance_lines})
                folio_id.write(vals)
        else:
            folio_id = super(insurance_folio, self).create(vals)
        return folio_id

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        '''
        When you change warehouse it will update the warehouse of
        the hotel folio as well
        ----------------------------------------------------------
        @param self : object pointer
        '''
        for folio in self:
            order = folio.order_id
            x = order.onchange_warehouse_id(folio.warehouse_id.id)
        return x


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        '''
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel folio as well
        ---------------------------------------------------------------
        @param self : object pointer
        '''
        if self.partner_id:
            partner_rec = self.env['res.partner'].browse(self.partner_id.id)
            order_ids = [folio.order_id.id for folio in self]
            if not order_ids:
                self.partner_invoice_id = partner_rec.id
                self.partner_shipping_id = partner_rec.id
                self.pricelist_id = partner_rec.property_product_pricelist.id
                raise Warning('Not Any Order For  %s ' % (partner_rec.name))
            else:
                self.partner_invoice_id = partner_rec.id
                self.partner_shipping_id = partner_rec.id
                self.pricelist_id = partner_rec.property_product_pricelist.id

    @api.multi
    def button_dummy(self):
        '''
        @param self : object pointer
        '''
        for folio in self:
            order = folio.order_id
            x = order.button_dummy()
        return x


    @api.multi
    def action_invoice_create(self,grouped=False, states=['confirmed', 'done']):
        '''
        @param self : object pointer
        '''
        order_ids = [folio.order_id.id for folio in self]
        sale_obj = self.env['sale.order'].browse(order_ids)
        invoice_id = sale_obj.action_invoice_create(grouped=False,states=['confirmed', 'done'])
        for line in self:
            values = {
                'invoiced': True,
                'state': 'progress' if grouped else 'progress',
            }
            line.write(values)
        return invoice_id


    @api.multi
    def action_invoice_cancel(self):
        '''
        @param self : object pointer
        '''
        order_ids = [folio.order_id.id for folio in self]
        sale_obj = self.env['sale.order'].browse(order_ids)
        res = sale_obj.action_invoice_cancel()
        for sale in self:
            for line in sale.order_line:
                line.write({'invoiced': 'invoiced'})
        sale.write({'state':'invoice_except'})
        return res

    @api.multi
    def action_cancel(self):
        '''
        @param self : object pointer
        '''
        order_ids = [folio.order_id.id for folio in self]
        sale_obj = self.env['sale.order'].browse(order_ids)
        rv = sale_obj.action_cancel()
        wf_service = netsvc.LocalService("workflow")
        for sale in self:
            for pick in sale.picking_ids:
               wf_service.trg_validate(self._uid, 'stock.picking', pick.id, 'button_cancel', self._cr)
            for invoice in sale.invoice_ids:
                wf_service.trg_validate(self._uid, 'account.invoice', invoice.id, 'invoice_cancel', self._cr)
                sale.write({'state':'cancel'})
        return rv

    @api.multi
    def action_wait(self):
        '''
        @param self : object pointer
        '''
        sale_order_obj = self.env['sale.order']
        res = False
        for o in self:
            sale_obj = sale_order_obj.browse([o.order_id.id])
            res = sale_obj.action_wait()
            if (o.order_policy == 'manual') and (not o.invoice_ids):
                o.write({'state': 'manual'})
            else:
                o.write({'state': 'progress'})
        return res


    @api.multi
    def test_state(self,mode):
        '''
        @param self : object pointer
        @param mode : state of workflow
        '''
        write_done_ids = []
        write_cancel_ids = []
        if write_done_ids:
            test_obj = self.env['sale.order.line'].browse(write_done_ids)
            test_obj.write({'state': 'done'})
        if write_cancel_ids:
            test_obj = self.env['sale.order.line'].browse(write_cancel_ids)
            test_obj.write({'state': 'cancel'})

    @api.multi
    def action_ship_create(self):
        '''
        @param self : object pointer
        '''
        for folio in self:
            order = folio.order_id
            x = order.action_ship_create()
        return x

    @api.multi
    def action_ship_end(self):
        '''
        @param self : object pointer
        '''
        order_ids = [folio.order_id.id for folio in self]
        for order in self:
            order.write ({'shipped':True})

    @api.multi
    def has_stockable_products(self):
        '''
        @param self : object pointer
        '''
        for folio in self:
            order = folio.order_id
            x = order.has_stockable_products()
        return x

    @api.multi
    def action_cancel_draft(self):
        '''
        @param self : object pointer
        '''
        if not len(self._ids):
            return False
        query = "select id from sale_order_line where order_id IN %s and state=%s"
        self._cr.execute(query, (tuple(self._ids), 'cancel'))
        cr1 = self._cr
        line_ids = map(lambda x: x[0],cr1.fetchall())
        self.write({'state': 'draft', 'invoice_ids': [], 'shipped': 0})
        sale_line_obj = self.env['sale.order.line'].browse(line_ids)
        sale_line_obj.write({'invoiced': False, 'state': 'draft', 'invoice_lines': [(6, 0, [])]})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in self._ids:
            # Deleting the existing instance of workflow for SO
            wf_service.trg_delete(self._uid,'sale.order', inv_id,self._cr)
            wf_service.trg_create(self._uid,'sale.order', inv_id,self._cr)
        for (id, name) in self.name_get():
            message = _("The sales order '%s' has been set in draft state.") % (name,)
            self.log(message)
        return True

class insurance_folio_line(models.Model):

    @api.one
    def copy(self,default=None):
        '''
        @param self : object pointer
        @param default : dict of default values to be set
        '''
        return self.env['sale.order.line'].copy(default=default)

    @api.multi
    def _amount_line(self,field_name, arg):
        '''
        @param self : object pointer
        @param field_name: Names of fields.
        @param arg: User defined arguments
        '''
        return self.env['sale.order.line']._amount_line(field_name, arg)

    @api.multi
    def _number_packages(self,field_name, arg):
        '''
        @param self : object pointer
        @param field_name: Names of fields.
        @param arg: User defined arguments
        '''
        return self.env['sale.order.line']._number_packages(field_name, arg)

    @api.model
    def _get_policy_start(self):
        if 'policy_start' in self._context:
            return self._context['policy_start']
        return date.today()

    @api.model
    def _get_policy_end(self):
        if 'policy_end' in self._context:
            return self._context['policy_end']
        return date.today()

    _name = 'insurance.folio.line'
    _description = 'insurance folio line'

    order_line_id = fields.Many2one('sale.order.line',string='Order Line' ,required=True, delegate=True, ondelete='cascade')
    folio_id = fields.Many2one('insurance.folio',string='Invoice', ondelete='cascade')
    policy_start = fields.Date('Start Date', required=False,default = _get_policy_start)
    policy_end = fields.Date('End Date', required=False,default = _get_policy_end)
    date_select = fields.Selection([('week', 'Week'), ('day', 'Day'), ('month', 'Monh'), ('year', 'Year')], "Date Range Selection", default="day")
    date_length = fields.Integer("Date Length", default=0)
    insurance_company = fields.Many2one('insurance.confirm_details', delegate=True)

    @api.model
    def create(self,vals,check=True):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for hotel folio line.
        """
        if 'folio_id' in vals:
            folio = self.env["insurance.folio"].browse(vals['folio_id'])
            vals.update({'order_id':folio.order_id.id})
        return super(models.Model, self).create(vals)

    @api.multi
    def unlink(self):
        """
        Overrides orm unlink method.
        @param self: The object pointer
        @return: True/False.
        """
        sale_line_obj = self.env['sale.order.line']
        for line in self:
            if line.order_line_id:
                sale_unlink_obj = sale_line_obj.browse([line.order_line_id.id])
                sale_unlink_obj.unlink()
        return super(insurance_folio_line, self).unlink()

    @api.multi
    def uos_change(self, product_uos, product_uos_qty=0, product_id=None):
        '''
        @param self : object pointer
        '''
        for folio in self:
            line = folio.order_line_id
            x = line.uos_change(product_uos, product_uos_qty=0, product_id=None)
        return x

    @api.multi
    def product_id_change(self,pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):
        '''
        @param self : object pointer
        '''
        line_ids = [folio.order_line_id.id for folio in self]
        if product:
            sale_line_obj = self.env['sale.order.line'].browse(line_ids)
            return sale_line_obj.product_id_change(pricelist, product, qty=0,
                uom=False, qty_uos=0, uos=False, name='', partner_id=partner_id,
                lang=False, update_tax=True, date_order=False)

    @api.multi
    def product_uom_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False):
        '''
        @param self : object pointer
        '''
        if product:
            return self.product_id_change(pricelist, product, qty=0,
                uom=False, qty_uos=0, uos=False, name='', partner_id=partner_id,
                lang=False, update_tax=True, date_order=False)


    @api.onchange('policy_start','policy_end')
    def on_change_checkout(self):
        '''
        When you change policy_start or policy_end it will checked it
        and update the qty of hotel folio line
        -----------------------------------------------------------------
        @param self : object pointer
        '''
        if not self.policy_start:
            self.policy_start = date.today()
        if not self.policy_end:
            self.policy_end = date.today()
        qty = 1
        if self.policy_end < self.policy_start:
            raise except_orm(_('Warning'),_('End Date must be greater or equal to Start date'))
        if self.policy_start:
            diffDate = (datetime.strptime(self.policy_end, "%Y-%m-%d") - datetime.strptime(self.policy_start, "%Y-%m-%d") )
            qty = diffDate.days
            if qty == 0:
                qty = 1
        self.product_uom_qty = qty


    @api.multi
    def button_confirm(self):
        '''
        @param self : object pointer
        '''
        for folio in self:
            line = folio.order_line_id
            x = line.button_confirm()
        return x

    @api.multi
    def button_done(self):
        '''
        @param self : object pointer
        '''
        line_ids = [folio.order_line_id.id for folio in self]
        sale_line_obj = self.env['sale.order.line'].browse(line_ids)
        res = sale_line_obj.button_done()
        wf_service = netsvc.LocalService("workflow")
        res = self.write({'state':'done'})
        for line in self:
            wf_service.trg_write(self._uid, 'sale.order', line.order_line_id.order_id.id, self._cr)
        return res

    @api.one
    def copy_data(self,default=None):
        '''
        @param self : object pointer
        @param default : dict of default values to be set
        '''
        line_id = self.order_line_id.id
        sale_line_obj = self.env['sale.order.line'].browse(line_id)
        return sale_line_obj.copy_data(default=default)

class res_company(models.Model):
    _inherit = 'res.company'

    additional_hours = fields.Integer('Additional Hours', help="Provide the min hours value for Start Date.")

## vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
