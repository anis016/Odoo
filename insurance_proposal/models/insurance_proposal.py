# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012-Today Astrums Services Pvt. Ltd. (<http://www.astrums.com>)
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
from calendar import isleap
from datetime import date, timedelta, datetime
from insurance_folio import insurance_folio

class insurance_summary(models.Model):
    _name = 'insurance.summary'
#    _rec_name = 'order_id'
    _order = 'date_order'
    _description = 'insurance summary'

#    order_id = fields.Many2one('sale.order','Order',  delegate=True, required=True, ondelete='cascade')

    date_order = fields.Date(string = "Date Order")
    customer_details = fields.Char(string="Customer Details")
    vehicle_details = fields.Char(string="Vehicle Details")
    policy_period = fields.Char(string="Policy Period")
    policy_type = fields.Char(string="Policy Type")
    insu_company_name = fields.Char(string="Insurance Company")
    premium_amount = fields.Float(string="Premium Amount")
    commision = fields.Char(string="Commision")
    sales_person = fields.Char(string="Sales Person")
    amnt_total = fields.Float(compute='_calculate_total_amount')
    
    @api.multi
    def _calculate_total_amount(self):
        res = {}
        res = {
            'total' : 0.0
        }
        query = "select sum(premium_amount) from insurance_summary"
        self.env.cr.execute(query)
        result = [row[0] for row in self._cr.fetchall()]
        
        sum = 0
        for i in result:
            sum += i
        
        res['total'] = sum
        print sum
        print res
        self.amnt_total = sum
        return res
        

class insurance_folio(models.Model):
    _inherit = 'insurance.folio'
    _order = 'reservation_id desc'

    reservation_id = fields.Many2one(comodel_name='insurance.reservation',string='Reservation Id')

class insurance_reservation(models.Model):

    _name = "insurance.reservation"
    _rec_name = "proposal_no"
    _description = "Insurance Proposal"
    _order = 'proposal_no desc'
    _inherit = ['mail.thread']

    proposal_no = fields.Char('Proposal No', size=64,readonly=True, default=lambda obj: obj.env['ir.sequence'].get('insurance.reservation'))
    date_order = fields.Date('Date', required=True, readonly=False, states={'draft':[('readonly', False)]},default=lambda *a: date.today())
    warehouse_id = fields.Many2one('stock.warehouse','Company', readonly=False, required=True, default = 1, states={'draft':[('readonly', False)]})
    partner_id = fields.Many2one('res.partner','Customer Name' ,readonly=True, required=True, states={'draft':[('readonly', False)]})
    pricelist_id = fields.Many2one('product.pricelist','Scheme' ,required=False, readonly=True, states={'draft':[('readonly', False)]}, help="Pricelist for current reservation. ")
    partner_invoice_id = fields.Many2one('res.partner','Invoice Address' ,readonly=True, states={'draft':[('readonly', False)]}, help="Invoice address for current reservation. ")
    partner_order_id = fields.Many2one('res.partner','Ordering Contact',readonly=True, states={'draft':[('readonly', False)]}, help="The name and address of the contact that requested the order or quotation.")
    partner_shipping_id = fields.Many2one('res.partner','Delivery Address' ,readonly=True, states={'draft':[('readonly', False)]}, help="Delivery address for current reservation. ")

    #policy_line = fields.One2many('insurance_reservation.line','line_id','Policy Line',help='Different Company Policy Details. ')
    state = fields.Selection([('draft', 'Book/Draft'), ('confirm', 'Confirm'), ('cancel', 'Cancel'), ('done', 'Done')], 'State', readonly=True,default=lambda *a: 'draft')

    coverage = fields.Selection([('comprehensive', 'Comprehensive'), ('tpft', 'TPFT'), ('tpo', 'TPO')], 'Coverage', required=False, readonly=False,default=lambda *a: 'comprehensive')
    finance = fields.Char('Finance', size=64)
    vehicle_no = fields.Char('Vehicle No', size=64)
    vehicle = fields.Selection([('private', 'Private Car'), ('commercial', 'Commercial Vehicle'), ('motor', 'Motor Cycle')], 'Vehicle', required=False, readonly=False,default=lambda *a: 'private')
    vehicle_make = fields.Char('Make', size=64)
    vehicle_model = fields.Char('Model', size=64)
    vehicle_type = fields.Selection([('normal', 'Normal Car'), ('offpeak', 'Off Peak Car')], 'Type', required=False, readonly=False,default=lambda *a: 'normal')
    parallal_import = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Parallal Import', required=False, readonly=False,default=lambda *a: 'no')
    sum_insured = fields.Integer('Sum Insured', size=64)
    y_o_m = fields.Char("Year of Manufacture ", size=24)
    reg_date = fields.Date("Original Reg. Date")
    capacity = fields.Integer('Capacity')
    seats = fields.Integer('No of Seaters')
    laden_weight = fields.Integer('Laden Weight')
    unladen_weight = fields.Integer('Unladen Weight')
    previous_insurer = fields.Char('Previous Insurer', size=64)
    ncd_entitlement = fields.Char('NCD Entitlement', size=64)
    
    any_claim = fields.Selection([('yes', 'Yes'), ('no', 'No')], 'Any Claim exp. pass 3 years', required=False, readonly=False,default=lambda *a: 'no')
    notes = fields.Text('Notes')

    folio_id = fields.Many2many('insurance.folio','insurance_folio_reservation_rel','order_id','invoice_id',string='Invoice ID')
    reservation_line = fields.One2many('insurance_company.line','line_id','Proposal Line',help='Companies Proposal for Insurance')
    dummy = fields.Date('Dummy')

    policy_start = fields.Date('Policy Start Date', required=True, readonly=False, states={'draft':[('readonly', False)]},default=lambda *a: date.today())
    policy_end = fields.Date('Policy End Date', readonly=False, store=True, compute = '_get_end_date')
    date_select = fields.Selection([('week', 'Week'), ('day', 'Day'), ('month', 'Month'), ('year', 'Year')], "Date Range Selection", default="day")
    date_length = fields.Integer("Date Length", default=0)

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


    @api.onchange('date_order','policy_start')
    def on_change_policy_start(self):
        '''
        When you change date_order or checkin it will check whether
        Checkin date should be greater than the current date
        -------------------------------------------------------------
        @param self : object pointer
        @return : raise warning depending on the validation
        '''
        policy_start_date=date.today()
        if self.date_order and self.policy_start:
            if self.policy_start < self.date_order:
                raise except_orm(_('Warning'),_('Policy Start date should be greater than the current date.'))


    @api.onchange('policy_end','policy_start')
    def on_change_policy_end(self):
      '''
      When you change cpolicy_endheckout or checkin it will check whether
      Checkout date should be greater than Checkin date
      and update dummy field
      -------------------------------------------------------------
      @param self : object pointer
      @return : raise warning depending on the validation
      '''
      policy_end_date=date.today()
      policy_start_date=date.today()
      res = {}
      if not (policy_end_date and policy_start_date):
            return {'value':{}}
      if self.policy_end and self.policy_start:
          if self.policy_end < self.policy_start:
                    raise except_orm(_('Warning'),_('Policy End date should be greater than Policy Start date.'))
      addDays = policy_end_date + timedelta(days=0)
      self.dummy = addDays


    @api.onchange('partner_id')
    def onchange_partner_id(self):
        '''
        When you change partner_id it will update the partner_invoice_id,
        partner_shipping_id and pricelist_id of the hotel reservation as well
        ----------------------------------------------------------------------
        @param self : object pointer
        '''
        if not self.partner_id:
            self.partner_invoice_id = False
            self.partner_shipping_id=False
            self.partner_order_id=False
        else:
            partner_lst = [self.partner_id.id]
            addr = self.partner_id.address_get(['delivery', 'invoice', 'contact'])
            self.partner_invoice_id = addr['invoice']
            self.partner_order_id = addr['contact']
            self.partner_shipping_id = addr['delivery']
            self.pricelist_id=self.partner_id.property_product_pricelist.id

    @api.multi
    def action_for_insurance(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(self._ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('insurance_reservation', 'email_template_insurance_reservation')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'insurance.reservation',
            'default_res_id': self._ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.cr_uid_ids_context
    def action_for_confirm(self, cr, uid, picking, context=None):
        if not context:
            context = {}
        print "Active ID Picking"
        print picking
        print "End of active ID"
        context.update({
            'active_model': self._name,
            'active_ids': picking,
            'active_id': len(picking) and picking[0] or False
        })
        print "Action for confirm"
        print len(picking)
        print picking[0]
        print "End of length of picking"

        created_id = self.pool['insurance.confirm_details'].create(cr, uid, {'picking_id': picking[0] or False}, context)
        return self.pool['insurance.confirm_details'].wizard_view(cr, uid, created_id, context)

    @api.multi
    def _create_insurance_summary(self, insurance_reservation_id, folio_id):
        res = {}

        insurance_reservation_obj = self.env['insurance.reservation'].browse(insurance_reservation_id)
        insurance_folio_obj = self.env['insurance.folio'].browse(folio_id)

        for res_record_id in insurance_reservation_obj:
            vehicle_no = str(res_record_id.vehicle_no) + "\n" + str(res_record_id.vehicle_model)
            res = {
                'vehicle_details': vehicle_no,
                'warehouse_id':res_record_id.warehouse_id.id,
                'pricelist_id':res_record_id.pricelist_id.id,
                'partner_invoice_id':res_record_id.partner_invoice_id.id,
                'partner_shipping_id':res_record_id.partner_shipping_id.id,
                'policy_type' : res_record_id.coverage,
            }

        for folio_record_id in insurance_folio_obj:
            str_date = folio_record_id.policy_start + " ~ " + folio_record_id.policy_end
            res_line = {
                'date_order' : folio_record_id.date_order,
                'customer_details' : folio_record_id.partner_id.name,
                'policy_period' : str_date,
                'insu_company_name' : folio_record_id.ins_company,
                'premium_amount' : folio_record_id.ins_amount,
                'commision' : folio_record_id.ins_amount, # need to update for commission
                'sales_person' : folio_record_id.user_id.name,
                'partner_id' : folio_record_id.partner_id.id,
            }
        res.update(res_line)
        insurance_summary_obj = self.env['insurance.summary']
        summary_id = insurance_summary_obj.create(res)

        return True


    @api.multi
    def create_insurance_folio(self):
        """
        This method is for create new insurance folio.
        -----------------------------------------
        @param self: The object pointer
        @return: new record set for insurance folio.
        """
        insurance_folio_obj = self.env['insurance.folio']
        for reservation in self:
            # find the id of the insurance_confirm_details
            insurance_confirm_obj = self.env['insurance.confirm_details']
            insurance_confirm_id = insurance_confirm_obj.search([('picking_id', '=', reservation.id)])

            product_obj = self.env['product.product'].browse(insurance_confirm_id.product_id.id)

            folio_lines = []
            policy_start, policy_end = reservation['policy_start'], reservation['policy_end']
            if not self.policy_start < self.policy_end:
                raise except_orm(_('Error'), _('Invalid values in Booking.\nEnd date should be greater than the Start date.'))
            duration_vals = self.onchange_check_dates(policy_start=policy_start, policy_end=policy_end, duration=False)
            duration = duration_vals.get('duration') or 0.0
            folio_vals = {
                'date_order':reservation.date_order,
                'warehouse_id':reservation.warehouse_id.id,
                'partner_id':reservation.partner_id.id,
                'pricelist_id':reservation.pricelist_id.id,
                'partner_invoice_id':reservation.partner_invoice_id.id,
                'partner_shipping_id':reservation.partner_shipping_id.id,
                'policy_start': reservation.policy_start,
                'policy_end': reservation.policy_end,
                'duration': duration,
                'reservation_id': reservation.id,
                'date_select': reservation.date_select,
                'date_length': reservation.date_length,
                'insurance_company': insurance_confirm_id.id
              # 'service_lines':reservation['folio_id']
            }

            for picking_id in insurance_confirm_id.picking_id:
                    folio_lines.append((0, 0, {
                        #'company_id': line.company_id.id,
                        #'line_id': line.line_id.id,
                        #'amount': line.amount,
                        'product_id': product_obj and product_obj.id,
                        'product_uom': product_obj.product_tmpl_id.uom_id.id,
                        #'price_unit': product_obj.product_tmpl_id.lst_price,
                        #'product_uom_qty': (reservation['policy_end'] - reservation['policy_start']).days,
                        'price_unit': insurance_confirm_id.amount,
                        'policy_start': picking_id.policy_start,
                        'policy_end': picking_id.policy_end,
                        'date_select': reservation.date_select,
                        'date_length': reservation.date_length,
                        'name': reservation['proposal_no'],
                        'insurance_company': insurance_confirm_id.id
                    }))
            folio_vals.update({'insurance_lines': folio_lines})
            folio = insurance_folio_obj.create(folio_vals)
            self._cr.execute('insert into insurance_folio_reservation_rel (order_id, invoice_id) values (%s,%s)', (reservation.id, folio.id))
            flag = reservation.write({'state': 'done'})
            if flag:
                self._create_insurance_summary(insurance_reservation_id = reservation.id, folio_id = folio.id)
                #sale_order_obj = self.env['sale.order']
                #ids = sale_order_obj.search([('id', '=', summary_id.order_id.id)])
            #    sale_order_obj.search([('id', '=', summary_id.order_id.id)]).unlink()
                #summary_id.write({'order_id': folio.order_id.id})
        return True

    @api.multi
    def onchange_check_dates(self,policy_start=False, policy_end=False, duration=False):
        '''
        This method gives the duration between check in checkout if customer will leave only for some
        hour it would be considers as a whole day. If customer will checkin checkout for more or equal
        hours , which configured in company as additional hours than it would be consider as full days
        ---------------------------------------------------------------------------------------------
        @param self : object pointer
        @return : Duration and policy_end
        '''
        value = {}
        duration = 0
        if policy_start and policy_end:
            dur = datetime.strptime(policy_end, '%Y-%m-%d') - datetime.strptime(policy_start, '%Y-%m-%d')
            duration = dur.days
        value.update({'duration':duration})
        return value

class insurance_company(models.Model):

    _name = 'insurance.company'
    _description = 'Insurance Companies'
    _rec_name = 'company_name'

    company_name = fields.Char('Insurance Company Name', size=64)
    company_address = fields.Char('Insurance Company Address', size=64)

class insurance_company_line(models.Model):

    _name = 'insurance_company.line'
    _description = 'Insurance Companies Line'

    line_id = fields.Many2one('insurance.reservation')
    amount = fields.Float('Proposed Amount')
    company_id = fields.Many2one('insurance.company','Company Name',help='Companies for Proposal.')


    # @api.multi
    # def send_my_maill(self):
    #     """Generates a new mail message for the Reservation template and schedules it,
    #        for delivery through the ``mail`` module's scheduler.
    #        @param self: The object pointer
    #     """
    #     template_id = self.env['email.template'].search([('name','=','Reservation-Send by Email')])
    #     for user in self:
    #         if not user.partner_id.email:
    #             raise except_orm(("Cannot send email: user has no email address."), user.partner_id.name)
    #         myobj = self.env['email.template'].browse(template_id.id)
    #         myobj.send_mail(user.id, force_send=True, raise_exception=True)
    #     return True

    # @api.multi
    # def action_for_hotel(self):
    #     '''
    #     This function opens a window to compose an email, with the edi sale template message loaded by default
    #     '''
    #     assert len(self._ids) == 1, 'This option should only be used for a single id at a time.'
    #     ir_model_data = self.env['ir.model.data']
    #     try:
    #         template_id = ir_model_data.get_object_reference('hotel_reservation', 'email_template_hotel_reservation')[1]
    #     except ValueError:
    #         template_id = False
    #     try:
    #         compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
    #     except ValueError:
    #         compose_form_id = False
    #     ctx = dict()
    #     ctx.update({
    #         'default_model': 'hotel.reservation',
    #         'default_res_id': self._ids[0],
    #         'default_use_template': bool(template_id),
    #         'default_template_id': template_id,
    #         'default_composition_mode': 'comment',
    #         'mark_so_as_sent': True
    #     })
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_type': 'form',
    #         'view_mode': 'form',
    #         'res_model': 'mail.compose.message',
    #         'views': [(compose_form_id, 'form')],
    #         'view_id': compose_form_id,
    #         'target': 'new',
    #         'context': ctx,
    #     }


## vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
