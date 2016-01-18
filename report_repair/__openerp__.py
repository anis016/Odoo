# -*- coding: utf-8 -*-
{
    'name': "report_repair",

    'summary': """
        For A&L Repair Invoice report""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PyKod",
    'website': "http://www.pykod.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'repair_mgmt'],
    "init_xml": [],
    # always loaded
    'update_xml': [
        # 'security/ir.model.access.csv',
        'anl_repair_report.xml',
        'views/report_anl_invoice.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}