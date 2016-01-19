# -*- coding: utf-8 -*-
{
    'name': "MK Holdings Report",

    'summary': """
        For MK Holdings Report""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PyKod",
    'website': "http://www.pykod.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],
    "init_xml": [],
    # always loaded
    'update_xml': [
        # 'security/ir.model.access.csv',
        'mk_holdings_report.xml',
        'views/report_mkholdings_sales.xml',
        'views/report_mkholdings_invoice.xml',
        'views/report_mkholdings_delivery.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
