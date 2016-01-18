# -*- coding: utf-8 -*-

from openerp import models, fields, api,_
from openerp.exceptions import except_orm, Warning
from openerp import netsvc

class repair_mgmt(models.Model):
    _name = 'repair.mgmt'
    _description = 'Vehicle Repair Management'
    _rec_name = 'order_id'
    _order = 'id desc'

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

    name = fields.Char('Booking Number', size=24, default=lambda obj:obj.env['ir.sequence'].get('repair.mgmt'), readonly=True)
    order_id = fields.Many2one('sale.order', 'Order', delegate=True, ondelete='cascade')
    room_lines = fields.One2many('repair.mgmt.line','repair_id', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, help="Vehicles Repair detail.")
    vehicles = fields.Many2one('product.product', 'Vehicles', required=True)

    @api.constrains('start_date','end_date')
    def check_dates(self):
        '''
        This method is used to validate the start_date and end_date.
        -------------------------------------------------------------------
        @param self : object pointer
        @return : raise warning depending on the validation
        '''
        if self.start_date >= self.end_date:
                raise except_orm(_('Warning'),_('Start Date Should be less than the End Date!'))

    @api.model
    def create(self, vals,check=True):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for hotel folio.
        """
        tmp_repair_lines = vals.get('room_lines', [])
        if 'repair_id' in vals:
                vals.update({'room_lines':[]})
                repair_id = super(repair_mgmt, self).create(vals)
                for line in (tmp_repair_lines):
                    line[2].update({'repair_id':repair_id})
                vals.update({'room_lines':tmp_repair_lines})
                repair_id.write(vals)
        else:
            repair_id = super(repair_mgmt, self).create(vals)
        return repair_id

    @api.onchange('warehouse_id')
    def onchange_warehouse_id(self):
        '''
        When you change warehouse it will update the warehouse of
        the hotel folio as well
        ----------------------------------------------------------
        @param self : object pointer
        '''
        for repair in self:
            order = repair.order_id
            x = order.onchange_warehouse_id(repair.warehouse_id.id)
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
        if self.product_id:
            sale_obj['vehicles'] = self.vehicles # Update the vehicles in sale
        invoice_id = sale_obj.action_invoice_create(grouped=False,states=['confirmed', 'done'])
        if self.product_id:
            sale_obj.invoice_ids['vehicles'] = self.vehicles # Update the vehicles in invoice
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

class repair_mgmt_line(models.Model):

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

    _name = 'repair.mgmt.line'
    _description = 'Vehicle Repair Management Line'

    order_line_id = fields.Many2one('sale.order.line',string='Order Line' ,required=True, delegate=True, ondelete='cascade')
    repair_id = fields.Many2one('repair.mgmt',string='Invoice', ondelete='cascade')
    start_date = fields.Date('Start Date', required=False)
    end_date = fields.Date('End Date', required=False)

    @api.model
    def create(self,vals,check=True):
        """
        Overrides orm create method.
        @param self: The object pointer
        @param vals: dictionary of fields value.
        @return: new record set for hotel folio line.
        """
        if 'repair_id' in vals:
            repair = self.env["repair.mgmt"].browse(vals['repair_id'])
            vals.update({'order_id':repair.order_id.id})
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
        return super(repair_mgmt_line, self).unlink()

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
