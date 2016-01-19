# -*- coding: utf-8 -*-
{
    'name': "Ming How Report",

    'summary': """
        For Ming How invoice Report""",

    'description': """
        Long description of module's purpose
    """,

    'author': "PyKod",
    'website': "http://www.pykod.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],
    "init_xml": [],
    # always loaded
    'update_xml': [
        # 'security/ir.model.access.csv',
        'ming_how_report.xml',
        'views/report_minghow_invoice.xml',
    ],
    'demo_xml': [],
    'installable': True,
    'active': False,
}
