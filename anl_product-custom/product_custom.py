# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 OpenERP SA (<http://www.serpentcs.com>)
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

class product_custom(osv.Model):
    _inherit = 'product.template'

    _columns = {

        # Client End Requirements
        'vehicle_no' : fields.char('Vehicle No ', size=128),
        'model' : fields.char('Model ', size=128),
        'engine_no' : fields.char('Engine No ', size=128),
        'chassis_no' : fields.char("Chassis No ", size=128),
        'y_o_m' : fields.char("Y.O.M ", size=24),
        'reg_date' : fields.date("Reg. Date"),
        'coe_expiry' : fields.date("C.O.E Expiry Date"),
        'parf' : fields.char("Parf", size=128),
        'non_parf' : fields.char("Non Parf", size=128),
        'company_reg' : fields.char("Company Registered", size=128),
        'no_of_transfer' : fields.char("No of Transfer", size=24),
        'capacity': fields.integer("Capacity/Seats"),

        # New Client requriements
        'roadtax_due_date' : fields.date(String="Road Tax date"),
        'inspect_due_date' : fields.date(String="Inspection date"),
        'mileage' : fields.char(String="Mileage"),

        'attachment' : fields.selection([('box', 'Box'), ('open', 'Open'),('canopy', 'Canopy')], 'Vehicle Attachment',default='box'),
        'deck' : fields.selection([('high', 'High'), ('low', 'Low')], 'Vehicle Deck', default='high'),

        'isvehicle':fields.boolean("Vehicle", default=False),
        }

    # def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
    #     res = super(res_partner, self).onchange_address(cr, uid, ids, use_parent_address, parent_id, context=context)
    #     if parent_id:
    #         parent = self.browse(cr, uid, parent_id, context=context)
    #         res['value'].update({'area' : parent.area or False})
    #     return res
    #
    # def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
    #     if not context:
    #         context = {}
    #     if context.get('no_own_company', False):
    #         company_obj = self.pool.get('res.company')
    #         company_ids = company_obj.search(cr, uid, [], context=context)
    #         company_recs = company_obj.browse(cr, uid, company_ids, context=context)
    #         partner_ids = [company.partner_id.id for company in company_recs]
    #         flag = False
    #         for domain in args:
    #             if domain[0] == 'id' and domain[1] == 'not in':
    #                 domain[2].extend(partner_ids)
    #                 flag = True
    #                 break
    #         if not flag:
    #             args.append(['id', 'not in', partner_ids])
    #
    #     return super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
