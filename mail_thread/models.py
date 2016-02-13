# -*- coding: utf-8 -*-

from openerp.osv import fields
from openerp.osv import osv
import logging
import base64
import time

_logger = logging.getLogger(__name__)

class mail_thread(osv.Model):
    _inherit = 'mail.thread'

    def message_track(self, cr, uid, ids, tracked_fields, initial_values, context=None):

        def convert_for_display(value, col_info):
            if not value and col_info['type'] == 'boolean':
                return 'False'
            if not value:
                return ''
            if col_info['type'] == 'many2one':
                return value.name_get()[0][1]
            if col_info['type'] == 'selection':
                return dict(col_info['selection'])[value]
            return value

        def format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, change in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % change.get('col_info')
                if change.get('old_value'):
                    message += '%s &rarr; ' % change.get('old_value')
                message += '%s</div>' % change.get('new_value')
            return message

        if not tracked_fields:
            return True

        for browse_record in self.browse(cr, uid, ids, context=context):
            initial = initial_values[browse_record.id]
            changes = set()
            tracked_values = {}

            product_line_value = ''
            # if browse_record.project_id:
            try:
                #product_line_value = '<div>%s</div>' % browse_record.project_id.name \
                #    + '<div>%s</div>' % browse_record.name

                print "browse.record: ", browse_record

                for order in browse_record:
                    for line in order.order_line:
               #         print "line.product_id: ", line.product_id
               #         print "line.product_uom_qty", line.product_uom_qty
               #         print "line.price_unit", line.price_unit
               #         print "line.sub_total", float(line.product_uom_qty) * float(line.price_unit)
               #         print "\n"
                        product_line_value += '<div><b>&nbsp; &nbsp; &bull; Product Name: </b>%s  <b>Quantity: </b>%s <b>Unit Price: </b>%s <b>Total: </b>%s </div>' %(line.product_id.name, line.product_uom_qty, line.price_unit, (float(line.product_uom_qty) * float(line.price_unit)))
            except:
                product_line_value = product_line_value
            
            try:
                print "Inside the attachment body"    
            except:
                print "Cant do anything."

            # generate tracked_values data structure: {'col_name': {col_info, new_value, old_value}}
            for col_name, col_info in tracked_fields.items():
                field = self._fields[col_name]
                initial_value = initial[col_name]
                record_value = getattr(browse_record, col_name)

                if record_value == initial_value and getattr(field, 'track_visibility', None) == 'always':
                    tracked_values[col_name] = dict(
                        col_info=col_info['string'],
                        new_value=convert_for_display(record_value, col_info),
                    )
                elif record_value != initial_value and (record_value or initial_value):  # because browse null != False
                    if getattr(field, 'track_visibility', None) in ['always', 'onchange']:
                        tracked_values[col_name] = dict(
                            col_info=col_info['string'],
                            old_value=convert_for_display(initial_value, col_info),
                            new_value=convert_for_display(record_value, col_info),
                        )
                    if col_name in tracked_fields:
                        changes.add(col_name)
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtypes = []
            # By passing this key, that allows to let the subtype empty and so don't sent email because partners_to_notify from mail_message._notify will be empty
            if not context.get('mail_track_log_only'):
                for field, track_info in self._track.items():
                    if field not in changes:
                        continue
                    for subtype, method in track_info.items():
                        if method(self, cr, uid, browse_record, context):
                            subtypes.append(subtype)

            posted = False
            for subtype in subtypes:
                subtype_rec = self.pool.get('ir.model.data').xmlid_to_object(cr, uid, subtype, context=context)
                if not (subtype_rec and subtype_rec.exists()):
                    _logger.debug('subtype %s not found' % subtype)
                    continue
                message = product_line_value + format_message(subtype_rec.description if subtype_rec.description else subtype_rec.name, tracked_values)
                self.message_post(cr, uid, browse_record.id, body=message, subtype=subtype, context=context)
                posted = True
            if not posted:
                message = format_message(product_line_value, tracked_values)
                self.message_post(cr, uid, browse_record.id, body=message, context=context)
        return True