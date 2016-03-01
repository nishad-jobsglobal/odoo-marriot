from datetime import timedelta
from openerp import models, fields, api, _
from openerp.tools import amount_to_text
from openerp.osv import osv

import time
from openerp.report import report_sxw

class account_invoice(models.Model):
    _inherit = "account.invoice"
    @api.multi
    def amount_to_text(self, amount, currency='AED'):
        dwo = amount_to_text(amount, 'en', currency)
        
        dwo = dwo.replace("and Zero Cent", "")
        
        if currency == 'AED' or currency == 'KWD':
            dwo = dwo.replace(" Cent", " Fil")
        elif currency == 'SAR':
            dwo = dwo.replace(" Cent", " Halala") 
            
        return dwo + " only"
        
        
    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False):
        ret = super(account_invoice, self).onchange_partner_id(
            type=type, partner_id=partner_id, date_invoice=date_invoice,
            payment_term=payment_term, partner_bank_id=partner_bank_id,
            company_id=company_id)
        if 'value' not in ret:
            ret['value'] = {}
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            ret['value']['user_id'] = partner.user_id.id or self.env.uid
        else:
            ret['value']['user_id'] = self.env.uid
        return ret


class Overdue_custom(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(Overdue_custom, self).__init__(cr, uid, name, context=context)
        ids = context.get('active_ids')
        partner_obj = self.pool['res.partner']
        docs = partner_obj.browse(cr, uid, ids, context)

        due = {}
        paid = {}
        mat = {}

        for partner in docs:
            due[partner.id] = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['debit'] or 0) or (y['account_id']['type'] == 'payable' and y['credit'] * -1 or 0)), self._lines_get(partner), 0)
            paid[partner.id] = reduce(lambda x, y: x + ((y['account_id']['type'] == 'receivable' and y['credit'] or 0) or (y['account_id']['type'] == 'payable' and y['debit'] * -1 or 0)), self._lines_get(partner), 0)
            mat[partner.id] = reduce(lambda x, y: x + (y['debit'] - y['credit']), filter(lambda x: x['date_maturity'] < time.strftime('%Y-%m-%d'), self._lines_get(partner)), 0)

        addresses = self.pool['res.partner']._address_display(cr, uid, ids, None, None)
        self.localcontext.update({
            'docs': docs,
            'time': time,
            'getLines': self._lines_get,
            'tel_get': self._tel_get,
            'message': self._message,
            'due': due,
            'paid': paid,
            'mat': mat,
            'addresses': addresses
        })
        self.context = context

    def _tel_get(self,partner):
        if not partner:
            return False
        res_partner = self.pool['res.partner']
        addresses = res_partner.address_get(self.cr, self.uid, [partner.id], ['invoice'])
        adr_id = addresses and addresses['invoice'] or False
        if adr_id:
            adr=res_partner.read(self.cr, self.uid, [adr_id])[0]
            return adr['phone']
        else:
            return partner.phone or False
        return False

    def _lines_get(self, partner):
        moveline_obj = self.pool['account.move.line']
        movelines = moveline_obj.search(self.cr, self.uid,
                [('partner_id', '=', partner.id),
                    ('account_id.type', 'in', ['receivable', 'payable']),
                    ('state', '<>', 'draft'), ('reconcile_id', '=', False)])
        movelines = moveline_obj.browse(self.cr, self.uid, movelines)
        return movelines

    def _message(self, obj, company):
        company_pool = self.pool['res.company']
        message = company_pool.browse(self.cr, self.uid, company.id, {'lang':obj.lang}).overdue_msg
        return message.split('\n')


        
class report_overdue_pcur(osv.AbstractModel):
    _name = 'report.account.report_overdue_pcur'
    _inherit = 'report.abstract_report'
    _template = 'account.report_overdue_pcur'
    _wrapped_report_class = Overdue_custom
    


