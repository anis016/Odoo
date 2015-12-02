# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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

from openerp import models, fields, api
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import except_orm, Warning

class insurance_confirm_details(models.Model):
    _name = 'insurance.confirm_details'
    _description = 'Insurance Confirm Details'


    picking_id = fields.Many2one('insurance.reservation', 'Picking')
    amount = fields.Float('Proposed Amount')
    company_id = fields.Many2one('insurance.company','Company Name',help='Companies for Proposal.')
    product_id = fields.Many2one('product.product','Which Insurance')
    reservation_line = fields.One2many('insurance_company.line','line_id','Proposal Line',help='Companies Proposal for Insurance')
    item_ids = fields.One2many('insurance.transfer_details_items', 'transfer_id', 'Items')

    # picking_id = fields.Many2one('stock.picking', 'Picking')
    # item_ids = fields.One2many('stock.transfer_details_items', 'transfer_id', 'Items', domain=[('product_id', '!=', False)])
    # packop_ids = fields.One2many('stock.transfer_details_items', 'transfer_id', 'Packs', domain=[('product_id', '=', False)])
    # picking_source_location_id = fields.Many2one('stock.location', string="Head source location", related='picking_id.location_id', store=False, readonly=True)
    # picking_destination_location_id = fields.Many2one('stock.location', string="Head destination location", related='picking_id.location_dest_id', store=False, readonly=True)

    def default_get(self, cr, uid, fields, context=None):
        if context is None: context = {}
        res = super(insurance_confirm_details, self).default_get(cr, uid, fields, context=context)

        picking_ids = context.get('active_ids', [])
        active_model = context.get('active_model')

        if not picking_ids or len(picking_ids) != 1:
            # Partial Picking Processing may only be done for one picking at a time
            return res
        assert active_model in ('insurance.reservation'), 'Bad context propagation'
        picking_id, = picking_ids
        picking = self.pool.get('insurance.reservation').browse(cr, uid, picking_id, context=context)
        items = []
        packs = []
        if not picking.reservation_line:
            return res
        for op in picking.reservation_line:
            print op.amount
            print op.company_id.id
            item = {
                'amount': op.amount,
                'company_id': op.company_id.id,
            }
            if True:
                items.append(item)
        #     if op.product_id:
        #         items.append(item)
        #     elif op.package_id:
        #         packs.append(item)
        res.update(item_ids=items)
        # res.update(packop_ids=packs)

        return res

    @api.multi
    def product_id_change(self, product, uom=False):
        result = {}
        if product:
            prod = self.env['product.product'].browse(product)
            result['product_uom_id'] = prod.uom_id and prod.uom_id.id
        return {'value': result, 'domain': {}, 'warning':{} }

    @api.multi
    def confirm_details(self):
        """
        This method create a new recordset for insurance reservation
        -------------------------------------------------------------------
        @param self: The object pointer
        @return: new record set for insurance reservation
        """
        company_line_obj = self.env['insurance_company.line']
        reservation_obj = self.env['insurance.reservation'].browse(self.picking_id.id)
        for reservation in reservation_obj:
            reservation.write({'state':'confirm'})
            self.write({'company_id': self.item_ids.company_id.id,
                            'amount': self.item_ids.amount})
        return True
  #              vals = {}
  #              for line_id in reservation.reservation_line:
  #                  if line_id.company_id.id == self.item_ids.company_id.id:
  #                      vals = {
  #                          'line_id': self.picking_id.id,
  #                          'amount': self.item_ids.amount,
  #                          'company_id': self.item_ids.company_id.id,
  #                      }
  #              ids = company_line_obj.search([('line_id', '=', self.picking_id.id)])
  #              print "ids of company_line_obj", ids
#                company_line_obj.search([('line_id', '=', self.picking_id.id)]).unlink()
 #               company_line_obj.create(vals)
        #reservation.send_my_maill()
        

    # @api.one
    # def do_detailed_transfer(self):
    #     processed_ids = []
    #     # Create new and update existing pack operations
    #     for lstits in [self.item_ids, self.packop_ids]:
    #         for prod in lstits:
    #             pack_datas = {
    #                 'product_id': prod.product_id.id,
    #                 'product_uom_id': prod.product_uom_id.id,
    #                 'product_qty': prod.quantity,
    #                 'package_id': prod.package_id.id,
    #                 'lot_id': prod.lot_id.id,
    #                 'location_id': prod.sourceloc_id.id,
    #                 'location_dest_id': prod.destinationloc_id.id,
    #                 'result_package_id': prod.result_package_id.id,
    #                 'date': prod.date if prod.date else datetime.now(),
    #                 'owner_id': prod.owner_id.id,
    #             }
    #             if prod.packop_id:
    #                 prod.packop_id.with_context(no_recompute=True).write(pack_datas)
    #                 processed_ids.append(prod.packop_id.id)
    #             else:
    #                 pack_datas['picking_id'] = self.picking_id.id
    #                 packop_id = self.env['stock.pack.operation'].create(pack_datas)
    #                 processed_ids.append(packop_id.id)
    #     # Delete the others
    #     packops = self.env['stock.pack.operation'].search(['&', ('picking_id', '=', self.picking_id.id), '!', ('id', 'in', processed_ids)])
    #     packops.unlink()

    #     # Execute the transfer of the picking
    #     self.picking_id.do_transfer()

    #     return True

    @api.multi
    def wizard_view(self):
        view = self.env.ref('insurance_proposal.view_insurance_enter_transfer_details')

        return {
            'name': _('Enter Confirmation details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'insurance.confirm_details',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': self.env.context,
        }

class insurance_details_items(models.TransientModel):
    _name = 'insurance.transfer_details_items'
    _description = 'Insurance Item Details'

    transfer_id = fields.Many2one('insurance.confirm_details', 'Transfer')
    amount = fields.Float('Proposed Amount')
    company_id = fields.Many2one('insurance.company','Company Name',help='Companies for Proposal.')
    product_id = fields.Many2one('product.product','Which Insurance')
