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

class res_partner(osv.Model):
    _inherit = 'res.partner'

    _columns = {
        'area' : fields.char('Area', size=128),
        'mcat_plan_no':fields.char('MCST Plan No.', size=128),
        'nea_license':fields.char('NRIC Number', size=128),
        'hp_no':fields.char("H/P", size=24),
        'd_o_b' :fields.date('Date of Birth'),
        'driver_license_number' :fields.char("Driver License Number", size=24),
        'driver_license_pass_date' :fields.date('Driver License Pass Date'),
        'gender':fields.selection([('male', 'Male'), ('female', 'Female')], 'Gender',default='male'),
        'marital':fields.selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')], 'Marital Status',default='single'),
        
        # Drivers address informations
        'dstreet': fields.char('Street'),
        'dstreet2': fields.char('Street2'),
        'dzip': fields.char('Zip', size=24, change_default=True),
        'dcity': fields.char('City'),
        'dstate_id': fields.many2one("res.country.state", 'State', ondelete='restrict'),
        'dcountry_id': fields.many2one('res.country', 'Country', ondelete='restrict'),
        }

    def onchange_address(self, cr, uid, ids, use_parent_address, parent_id, context=None):
        res = super(res_partner, self).onchange_address(cr, uid, ids, use_parent_address, parent_id, context=context)
        if parent_id:
            parent = self.browse(cr, uid, parent_id, context=context)
            res['value'].update({'area' : parent.area or False})
        return res

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None, count=False):
        if not context:
            context = {}
        if context.get('no_own_company', False):
            company_obj = self.pool.get('res.company')
            company_ids = company_obj.search(cr, uid, [], context=context)
            company_recs = company_obj.browse(cr, uid, company_ids, context=context)
            partner_ids = [company.partner_id.id for company in company_recs]
            flag = False
            for domain in args:
                if domain[0] == 'id' and domain[1] == 'not in':
                    domain[2].extend(partner_ids)
                    flag = True
                    break
            if not flag:
                args.append(['id', 'not in', partner_ids])

        return super(res_partner, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context, count=count)
