# -*- coding: utf-8 -*-
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

{
    "name" : "Insurance  - A&L",
    "version" : "0.01",
    "author": ["Austrums"],
    "category" : "Generic Modules/Insurance Management",
    "description": """
    Module for Insurance Management. You can manage:
    * Car Insurance

    """,
    "website": ["http://www.austrums.com.sg"],
    "depends" : ["base",'mail','email_template','sale_stock','stock','sale'],
    # "demo" : [
    #     "views/hotel_reservation_data.xml",
    # ],
    "data" : [
        "security/insurance_security.xml",
        "security/ir.model.access.csv",
        "views/insurance_confirm_details.xml",
        "views/insurance_proposal_sequence.xml",
        "views/insurance_proposal_view.xml",
        "views/insurance_folio_workflow.xml",
        "views/insurance_sequence.xml",
        "views/insurance_view.xml",
        "views/email_temp_view.xml",
        "views/insurance_summary.xml",
    ],
    # 'js': ["static/src/js/hotel_room_summary.js", ],
    # 'qweb': ['static/src/xml/hotel_room_summary.xml'],
    # 'css': ["static/src/css/room_summary.css"],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
