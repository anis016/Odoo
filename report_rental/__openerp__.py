{
    "name": "report_rental",
    "version": "1.0",
    "depends": ["base", "sale"],
    "author": "Sayed Anisul Hoque",
    "category": "Custom",
    'images': [],
    "description":""" This is for the AnL Rental Report """,
    "init_xml": [],
    'update_xml': [
                   'anl_rental_report.xml',
                   'views/report_anl_agreement.xml',
                   'views/report_anl_quotation.xml',
                   'views/report_anl_invoice.xml',
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,

}
