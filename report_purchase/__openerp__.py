# -*- coding: utf-8 -*-
{
    'name': "report_purchase",

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
    'depends': ['base', 'purchase'],
    "init_xml": [],
    # always loaded
    'update_xml': [
        # 'security/ir.model.access.csv',
        'anl_purchase_report.xml',
        'views/report_anl_quotation.xml',
        'views/report_anl_agreement.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}