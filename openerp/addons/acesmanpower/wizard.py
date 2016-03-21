# -*- coding: utf-8 -*-

from openerp import models 
from openerp.osv import orm
from openerp.osv import fields

class Wizard(models.TransientModel):
    _name = 'acesmanpower.wizard'
    
    def _default_jobseeker(self):
        return self.env['acesjobseeker'].browse(self._context.get('active_id'))
    
    def _default_get_gateway(self):
        gateway_ids = self.env['sms.smsclient'].search([])
        return gateway_ids and gateway_ids[0] or False

    def _default_validity(self):
        gateway_id = self.env['sms.smsclient'].search([])
        gateway = self.env['sms.smsclient'].browse(gateway_id[0])
        return gateway.validity or False
    
    def _default_classes(self):
        gateway_id = self.env['sms.smsclient'].search([])
        gateway = self.env['sms.smsclient'].browse(gateway_id[0])
        return gateway.classes or False
    
    def _default_deferred(self):
        gateway_id = self.env['sms.smsclient'].search([])
        gateway = self.env['sms.smsclient'].browse(gateway_id[0])
        return gateway.deferred or False
    
    def _default_coding(self):
        gateway_id = self.env['sms.smsclient'].search([])
        gateway = self.env['sms.smsclient'].browse(gateway_id[0])
        return gateway.coding or False
    
    def _default_tag(self):
        gateway_id = self.env['sms.smsclient'].search([])
        gateway = self.env['sms.smsclient'].browse(gateway_id[0])
        return gateway.tag or False
    
    def _default_nonstop(self):
        gateway_id = self.env['sms.smsclient'].search([])
        gateway = self.env['sms.smsclient'].browse(gateway_id[0])
        return gateway.nostop or False
          
    _columns = { 
                
        'jobseeker_id' : fields.many2one('acesjobseeker', string="Jobseeker", required=True, default=_default_jobseeker),
        'mobile_to' : fields.char(related='jobseeker_id.mobile', store=True, string='Mobile' ),
        'text' : fields.text(string="Message"),
        
        'gateway' : fields.many2one('sms.smsclient', string='SMS Gateway', default=_default_get_gateway),
        'validity' : fields.integer('Validity'),
        'classes' : fields.selection([
                    ('0', 'Flash'),
                    ('1', 'Phone display'),
                    ('2', 'SIM'),
                    ('3', 'Toolkit')
                ], 'Class', help='the sms class: flash(0), phone display(1), SIM(2), toolkit(3)'),
        'deferred' :  fields.integer('Deferred'),
        'priority' : fields.selection([
                    ('0','0'),
                    ('1','1'),
                    ('2','2'),
                    ('3','3')
                ], 'Priority', help='The priority of the message'),
        'coding' :  fields.selection([
                    ('1', '7 bit'),
                    ('2', 'Unicode')
                ], 'Coding', help='The SMS coding: 1 for 7 bit or 2 for unicode'),
        'tag' :  fields.char('Tag', size=520, help='an optional tag'),
        'nostop' :  fields.boolean('NoStop', help='Do not display STOP clause in the message, this requires that this is not an advertising message')
        
    }
    
    _defaults = {
        'validity': 10,
        'classes': '1',
        'deferred': 0, 
        'priority': '3',
        'coding': '1',
        'nostop': True,
    }
    
    def send_sms(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        client_obj = self.pool.get('sms.smsclient')
        for data in self.browse(cr, uid, ids, context=context):
            if not data.gateway:
                raise orm.except_orm(_('Error'), _('No Gateway Found'))
            else:
                client_obj._send_message(cr, uid, data, context=context)
        return {}
    
class WizardJobseeker(models.TransientModel):
    _name = 'acesmanpower.jobseeker.wizard'
    
    def _default_jobseeker(self):
        return self.env['acesjobseeker'].browse(self._context.get('active_id'))

    columns = {
               'jobseeker_id' : fields.many2one('acesjobseeker', string="Jobseeker", required=True, default=_default_jobseeker),
               'mobile' : fields.char(related='jobseeker_id.mobile', store=True, string='Mobile' ),
               'message' : fields.text(string="Message"),
               }
    
class WizardNotify(models.TransientModel):
    _name = 'acesmanpower.notify.agents'
    
    def _default_consultant(self):
        return self.env['acesmanpoweruser'].browse(self._context.get('active_id'))
    
    def _default_mobile_no(self):
        return self.env['acesmanpoweruser'].browse([self._context.get('active_id')]).mobile or 0000
    
    _columns = { 
            'agency_consultant_ids' : fields.many2one('acesmanpoweruser', string="Agency Consultant",default=_default_consultant),
            'mobile' : fields.char(size=12, string='Mobile', default=_default_mobile_no),
            'message' : fields.text(string="Message")
            }
    
    
class WizardNotify1(models.TransientModel):
    _name = 'acesmanpower.notifyassess'
    
    def _default_assess(self):
        return self.env['acesmanpowershortlist'].browse(self._context.get('active_id'))
    
    def _default_consultant(self):
        property_id = self._context.get('acesmanpowerproperty_id')
        agency_consultant_ids = [consultants.id for consultants in self.env['acesmanpowerproperty'].browse([property_id]).agency_consultant_ids]
        return {'value': {'agency_contacts': [(6, 0, agency_consultant_ids)]}}
    
    def _default_mobile_no(self):
        acesjobseeker_id = self.env['acesmanpowershortlist'].browse(self._context.get('active_id')).acesjobseeker_id.id
        return self.env['acesjobseeker'].browse([acesjobseeker_id]).mobile
    
    def on_change_consultant_id(self, cr, uid, ids, agency_consultant_id,context=None):
        mobile = self.pool.get('acesmanpoweruser').browse(cr,uid,[agency_consultant_id]).mobile or 000
        return {'value': {'mobile': mobile}}
    
    _columns = { 
            'acesmanpowershortlist_id' : fields.many2one('acesmanpowershortlist', "Applicant Process", default=_default_assess),
            'mobile' : fields.char(size=12, string='Mobile', default=_default_mobile_no),
            'message' : fields.text(string="Message")
            }
    
class WizardNotify2(models.TransientModel):
    _name = 'acesmanpower.notifyusers'
    
    
    def _default_partner(self):
        user_id =  self.env['acesmanpoweruser'].browse(self._context.get('active_id')).user_id.id
        return self.env['res.users'].browse([user_id]).partner_id.id
    
    def _default_mobile_no(self):
        user_id =  self.env['acesmanpoweruser'].browse(self._context.get('active_id')).user_id.id
        partner_id = self.env['res.users'].browse([user_id]).partner_id.id
        return self.env['res.partner'].browse([partner_id]).mobile or 000
    
    _columns = { 
            'recipient_id' : fields.many2one('res.partner', string="Send to", default=_default_partner),
            'mobile' : fields.char(size=12, string='Mobile', default=_default_mobile_no),
            'message' : fields.text(string="Message")
            }

class WizardNotify3(models.TransientModel):
    _name = 'acesmanpower.createuser'
    
    _columns = { 
            'name' : fields.char(string='Name' , required=True, ),
            'login' : fields.char(string='Login/Email' , required=True, ),
            'password' : fields.char(string='Password' , required=True, ),
            'mobile' : fields.char(string='Mobile', required=True, ),
            'property_id' : fields.many2one('acesmanpowerproperty', ondelete='set null', string="Default Property", index=True),
            'company_id' : fields.many2one('res.company', ondelete='set null', string="Company" , required=True,),
            'access_id' : fields.selection([('staff', 'Recruitment Staff'), ('manager', 'Recruitment Management'), ('admin', 'Administrator')], 'Role / Access Level', required=True,)
            }
   
class WizardSms(models.TransientModel):
    _name = 'acesmanpower.wizardsms'
    
    def _default_mobile(self):
        return self._context.get('mobile')
    
    def _default_sender(self):
        return self._context.get('sender')
        
    def _default_auser(self):
        return self._context.get('auser')    
    
    _columns = { 
            'mobile' : fields.char(string='Mobile', required=True, default=_default_mobile ),
            'sender' : fields.char(string='Sender', required=True, default=_default_sender ),
            'message' : fields.text(string="Message"),
            'auser_id' : fields.integer(string='', default=_default_auser)
            }
    