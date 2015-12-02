# -*- coding: utf-8 -*-
{
    'name': "report_sales",

    'summary': """
        For A&L Sales quotation report""",

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
        'anl_sales_report.xml',
        'views/report_anl_quotation.xml',
        'views/report_anl_agreement.xml',
        'views/report_anl_invoice.xml',
        'views/report_anl_delivery.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}