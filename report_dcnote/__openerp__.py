# -*- coding: utf-8 -*-
{
    'name': "Report for Debit and Credit",

    'summary': """
        For A&L Debit and Credit report""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PyKod",
    'website': "http://www.pykod.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],
    "init_xml": [],
    # always loaded
    'update_xml': [
        # 'security/ir.model.access.csv',
        'anl_debit_credit_report.xml',
        'views/report_anl_credit_note.xml',
        'views/report_anl_debit_note.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
