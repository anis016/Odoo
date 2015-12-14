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
    "name" : "Rental Management - A&L",
    "version" : "0.01",
    "author": ["Austrums" ],
    "category" : "Generic Modules/Rental Management",
    "description": """
    Module for Rent Management. You can manage:
    * Car Reservation
    * Car Rent
      Different reports are also provided, mainly for Rental statistics.
    """,
    "website": ["http://www.austrums.com.sg"],
    "depends" : ["sale_stock", "report_extended"],
    "data": [
        "security/hotel_security.xml",
        "security/ir.model.access.csv",
        "views/hotel_sequence.xml",
        "views/hotel_folio_workflow.xml",
#        "report/hotel_report.xml",
        "views/hotel_view.xml",
#        "views/hotel_data.xml",
        "wizard/hotel_wizard.xml",
        "views/hotel_report.xml",
        "views/report_hotel_management.xml",
    ],
    'css': ["static/src/css/room_kanban.css"],
    "auto_install": False,
    "installable": True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
