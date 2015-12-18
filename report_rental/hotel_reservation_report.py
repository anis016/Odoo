'''
Created on Nov 28, 2015

@author: anis
'''

from openerp import models
import time
from openerp.report import report_sxw

class hotel_reservation_report(report_sxw.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(hotel_reservation_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_dollar': self._get_dollar,
            'get_cent': self._get_cent,
            'get_total_amnt': self._get_total_amnt,
        })
        self.context = context
        
    def _get_total_amnt(self, amnt, length, deposit):
        total = amnt * length
        result = total - deposit
        return result
            
    def _get_dollar(self, amnt, length):
        res = float(amnt) * float(length) 
        con_str = str(res)
        y = con_str.split('.')
        return int(y[0])
        
    def _get_cent(self, amnt, length):
        res = float(amnt) * float(length)
        con_str = str(res)
        y = con_str.split('.')
        return int(y[1])
    
class report_decimal_checkin(models.AbstractModel):
    _name = "report.report_rental.report_anl_agreement"
    _inherit = "report.abstract_report"
    _template = "report_rental.report_anl_agreement"
    _wrapped_report_class = hotel_reservation_report