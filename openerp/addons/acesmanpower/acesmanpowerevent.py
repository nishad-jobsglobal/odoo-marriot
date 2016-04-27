# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Jobsglobal.com
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import base64
import urllib

from openerp import api
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from openerp.tools.translate import _
from psycopg2 import IntegrityError

class acesmanpowerevent(osv.osv):
    _name = 'acesmanpowerevent'
    _description = "Recruitment Event"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.v8
    def getdefaultpartner(self):
        return True
    
    @api.v8
    def get_urlencode(self, f1='a', v1='1', f2='b', v2='2', f3='c', v3='3'):
        f = { f1 : v1, f2 : v2, f3 : v3}
        return urllib.urlencode(f)
    
    @api.v8
    def get_quote(self, text):
        return urllib.quote(text)
    
    def getbase64(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        users = self.pool.get('res.users').browse(cr, uid, [uid])
        for w in self.browse(cr, uid, ids, context=context):
            for r in users:
                result[w.id] = base64.b64encode((str(uid) or '') + '---' + r.password)
        return result
    
    @api.multi
    def action_view_invite(self):
        return True
    
    @api.multi
    def action_view_participant(self):
        return True
    
    @api.multi
    def action_view_registration(self):
        return True
    
    def action_view_shortlists(self, cr, uid, ids,context=None):
        active_id = ids[0]
        shortlist_ids = self.pool.get('acesmanpowershortlist').search(cr,uid,[('acesmanpowerevent_id','=',active_id)])
        domain = [('id','in',shortlist_ids)]
        value = {
                'name': _("Shortlisted Candidates"),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesmanpowershortlist',
                'view_id': False,
                'domain': domain
                }
        return value
    
    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.stage_id != 'new':
                raise osv.except_osv(_('Warning!'),_('You can only delete draft records!'))
        return super(acesmanpowerevent, self).unlink(cr, uid, ids, context)
    
    @api.model
    def create(self,vals):
        
        new_id = super(acesmanpowerevent, self).create(vals)
        
        # Send SMS to the Property Group Manager for the approval of a trip. 
        self.env.cr.execute("SELECT id FROM res_groups WHERE name='Group Management'")
        group_id = self.env.cr.fetchone()[0]
        self.env.cr.execute("SELECT uid FROM res_groups_users_rel WHERE gid="+str(group_id))
        rst = self.env.cr.fetchall()
        if rst not in (None,[None],[]):
            for record in rst:
                if record[0] == 1:
                    continue
                manager_id = record[0]
                manager = self.env['acesmanpoweruser'].search([('user_id','=',manager_id)])
                
        # Send SMS to the manager    
            
        initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
        link = "http://64.71.72.30:8080/link.php?id=" + str(new_id.id)
        to = manager.mobile or 0
        mess = 'A new Recruitment Trip has been proposed by ' + initiator_obj.name + '.  Follow URL link to take action, ' + link
        
        thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
        ames={}
        ames['msg'] = mess
        ames['gateway_id'] = 1
        ames['mobile'] = to
        ames['name'] = thelink + "to=" + to + "&" + 'text=' + mess
        self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
        
        # Send Notification
        sysm = {}
        sysm['model'] = 'acesmanpowerevent'
        sysm['type'] = 'notification'
        sysm['subject'] = 'SMS'
        sysm['res_id'] = new_id.id
        sysm['body'] = 'Message has been sent'
        self.pool.get('mail.message').create(self._cr,SUPERUSER_ID,sysm)
        
        # Send mail to Manager to inform that a trip has been created and is waiting for approval.
        
        mail_server = None
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(self._cr, SUPERUSER_ID, [], order='sequence', limit=1)
        if mail_server_ids:
            mail_server = mail_server_obj.browse(self._cr, SUPERUSER_ID, mail_server_ids[0])
              
        if mail_server:
            body = subject = ''
            subject += "Recruitment Trip"
            url = (str('http://64.71.72.30:8080/web')+
                         "?db=%s#id=%d&view_type=form&model=acesmanpowerevent"%(self._cr.dbname,new_id.id))
            body += 'A new Recruitment Trip has been proposed by ' + initiator_obj.name + '.  Follow URL link to take action, ' + url
                
            sender_obj = self.env['res.users'].search([('id','=',self._uid)])
            sender_email =  sender_obj.login
            manager_obj = self.env['res.users'].search([('id','=',manager_id)])
            manager_email = manager_obj.login
            
            if sender_email and manager_email:
                try:
                    msg = mail_server_obj.build_email(
                                                    email_from = sender_email,
                                                    email_to = [manager_email],
                                                    subject = subject,
                                                    body = body,
                                                    subtype_alternative = 'plain')
                    res = mail_server_obj.send_email(self._cr, self._uid, msg,
                       mail_server_id=mail_server_ids[0])
                    
                except Exception:
                    return new_id
        return new_id
    
    def create_trip(self):
        
        event_obj = self.env['acesmanpowerevent'].search([('id','=',self.id)])
        manpower_user_obj = self.env['acesmanpoweruser']
        property_id = manpower_user_obj.browse([event_obj.acesmanpoweruser_id.id]).property_id.id
        partner_id = self.env['acesmanpowerproperty'].browse([property_id]).partner_id.id
        # Create new Trip details
        vals = {
              'name':event_obj.name,
              'trip_start':event_obj.datestart,
              'trip_end':event_obj.dateend,
              'property_id':property_id,
              'triptype':'trip',
              'can_country_id':event_obj.can_country_id.id,
              'partner_id':partner_id,
              'marriot_trip_id':self.id,
                }
        trip_id = self.env['trip'].create(vals)
        
        # Find all new jobs created in this event and create the same in Trip jobs
        job_ids = [obj.id for obj in event_obj.acesmanpowerjob_ids]
        if job_ids:
            for job_id in job_ids:
                job_obj = self.env['acesmanpowerjob'].browse([job_id])
                vals = {
                      'name':job_obj.name,
                      'description':job_obj.jobdescription or '',
                      'candidatesrequired':job_obj.quantity or 0,
                      'trip_id':trip_id.id,
                      }
                self.env['trjob'].create(vals)
                #job_obj.write({'approve':'approve'})
        
        # Add followers(who belong to processing team) to the newly created Trip 
        self.env.cr.execute("SELECT id FROM res_groups WHERE name='Member of Head office Processing Team'")
        group_id = self.env.cr.fetchone()[0]
        self.env.cr.execute("SELECT uid FROM res_groups_users_rel WHERE gid="+str(group_id))
        users=self.env.cr.fetchall()
        follower_ids = []
        for user_id in users:
            if not user_id[0] == self.env.uid:
                follower_ids.append(user_id[0])
        for user_id in follower_ids:
            partner_id = self.env['res.users'].browse([user_id]).partner_id.id
            followers = {
                        'res_model':'trip',
                        'res_id':trip_id.id,
                        'partner_id':partner_id
                        }
            try:
                self.env['mail.followers'].create(followers)
            except IntegrityError:
                continue
        return trip_id.id
    
    def send_notification_mail(self):
        
        # Send SMS to the manager    
        initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
        mobile = self.env['acesmanpowerevent'].search([('id','=',self.id)]).acesmanpoweruser_id.mobile

        to = mobile or 0
        mess = 'Your request for the Recruitment Trip has been denied by ' + initiator_obj.name
        thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
        ames={}
        ames['msg'] = mess
        ames['gateway_id'] = 1
        ames['mobile'] = to
        ames['name'] = thelink + "to=" + to + "&" + 'text=' + mess
        self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
        
        # Send mail to Manager to inform that a trip has been created and is waiting for approval.
        
        mail_server = None
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(self._cr, SUPERUSER_ID, [], order='sequence', limit=1)
        if mail_server_ids:
            mail_server = mail_server_obj.browse(self._cr, SUPERUSER_ID, mail_server_ids[0])
              
        if mail_server:
            body = subject = ''
            subject += "Recruitment Trip"
            body += 'Your request for the Recruitment Trip has been denied by ' + initiator_obj.name
             
            manager_obj = self.env['res.users'].search([('id','=',self._uid)])
            manager_email = manager_obj.login
            
            acesmanpoweruser_id = self.env['acesmanpowerevent'].search([('id','=',self.id)]).acesmanpoweruser_id.id
            rceiver_obj = self.env['res.users'].search([('acesmanpoweruser_id','=',acesmanpoweruser_id)])
            rceiver_email =  rceiver_obj.login
            
            if rceiver_email and manager_email:
                try:
                    msg = mail_server_obj.build_email(
                                                    email_from = manager_email,
                                                    email_to = [rceiver_email],
                                                    subject = subject,
                                                    body = body,
                                                    subtype_alternative = 'plain')
                    res = mail_server_obj.send_email(self._cr, self._uid, msg,
                        mail_server_id=mail_server_ids[0])
                except Exception:
                    return True
    
    @api.multi
    def write(self, values):
        stage_id = values.get('stage_id',False)
        
        # Validations for the event 
        
        flag_group_admin = self.env['res.users'].has_group('base.group_marriot_group_property_admin')
        if not flag_group_admin:
            if stage_id != 'new' and stage_id != False:
                raise osv.except_osv(_('Warning!'), _("You don't have the permission to change the stage of this trip. Please contact Group Manager"))
            elif stage_id == False and len(values) >= 1:
                raise osv.except_osv(_('Warning!'), _("You don't have the permission to change the details of this trip." 
                                                  " Please contact Group Manager"))
            elif stage_id == 'new':
                event_obj = self.env['acesmanpowerevent'].search([('id','=',self.id)])
                if event_obj.stage_id != 'new':
                    raise osv.except_osv(_('Warning!'), _("You don't have the permission to change the stage of this trip. Please contact Group Manager"))
        if flag_group_admin:
            # Find out if a trip is already created with respect to this event.
            marriot_trip_id = self.env['trip'].search([('marriot_trip_id','=',self.id)])
        else:
            marriot_trip_id = None

        numproperty = 0
        # Send SMS to all properties to inform an Event has been approved and if wish then join with them.
        properties = self.env['acesmanpowerproperty'].search([['mobile', '!=', '']])
        
        for property in properties:
            thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
            link = "http://64.71.72.30:8080/?id=" + str(self.id) + '%26pid=' + str(property.id)
            mess = 'Recruitment Trip,' + self.name + ' , has been approved. Follow URL link to take action, ' + link
            ames={}
            ames['msg'] = mess
            ames['gateway_id'] = 2
            ames['mobile'] = property.mobile
            ames['name'] = thelink + "to=" + property.mobile + "&" + 'text=' + mess
            #self.env['sms.smsclient.queue'].sudo().create(ames)
            self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
            numproperty += 1
            
        # Record mail_message in respective event.
        sysm = {}
        sysm['model'] = 'acesmanpowerevent'
        sysm['type'] = 'notification'
        sysm['subject'] = 'SMS'
        sysm['res_id'] = self.id
        sysm['body'] = 'Invitations has been sent to ' + str(numproperty) + ' properties'  
        #env['mail.message'].create(sysm)
        self.pool.get('mail.message').create(self._cr,SUPERUSER_ID,sysm)
            
        # Create a Trip in Human Resource -> Recruitment Trips -> Trips to do further follow ups.
        if not marriot_trip_id and stage_id == 'approved':
            trip_id = self.create_trip()
            values.update({'trip_id':trip_id})
        elif not marriot_trip_id and stage_id == 'disapproved':
            self.send_notification_mail()
            
        # Find the property linked with the trip initiator and add it to the joining properties.
        event_obj = self.env['acesmanpowerevent']
        property_id = event_obj.browse([self.id]).acesmanpoweruser_id.property_id.id
        if property_id:
            values['acesmanpowerproperty_ids'] = [(6, 0, [property_id])]
            
        #elif marriot_trip_id and not stage_id:
            # TO DO
        return super(acesmanpowerevent, self).write(values)

    _columns = {
            'name': fields.char(size=256, string='Name', required=True, ),
            'email': fields.char(size=100, string='Email', ),
            'mobile': fields.char(size=100, string='Mobile', ),
            'street': fields.char(size=256, string='Street', ),
            'city': fields.char(size=256, string='City', ),
            'can_country_id': fields.many2one('res.country', 'Recruit Location'),
            
            'stage_id': fields.selection([('new', 'New'),('approved', 'Approved'),('disapproved','Disapproved'),('done','Done'),('cancelled','Cancelled')], 'Status', track_visibility='onchange' ),
            'company_id': fields.many2one('res.company', 'Company'),
            'user_id': fields.many2one('res.users', 'Created User', readonly=True, ),
            'acesmanpoweruser_id': fields.related('user_id', 'acesmanpoweruser_id', type="many2one", relation="acesmanpoweruser", string="Recruitment User", store=True),
            'partner_id': fields.related('user_id', 'partner_id', type="many2one", relation="res.partner", string="Contact Person", store=True),
            
            'email': fields.related('user_id', 'email', type='char', size=256, string='Email', store=True),
            'mobile': fields.related('user_id', 'mobile', type='char', size=256, string='Mobile', store=True),
            'secu': fields.related('user_id', 'password', type='char', size=256, string='****', store=True, readonly=True),
            
            'datestart': fields.date(string='Start', ),
            'dateend': fields.date(string='End', ),
            
            'twitterhashtag': fields.char(size=100, string='Twitter Hash Tag', ),
            'color': fields.integer('Color Index'),
            'url_image': fields.char(size=500, string='Image url', ),
            'description': fields.text(string='Notes', ),
            
            'hr_job_ids': fields.many2many('hr.job','hr_job_acesmanpowerevent_rel', 'acesmanpowerevent_id', 'hr_job_id'),
            'acesmanpowerjob_ids': fields.one2many('acesmanpowerjob','acesmanpowerevent_id','Jobs'),
            'acesmanpowerproperty_ids': fields.many2many('acesmanpowerproperty','acesmproperty_acesmevent_rel', 'acesmanpowerevent_id', 'acesmanpowerproperty_id', string="Properties"),
            
            'create_date': fields.datetime('Create Date', readonly=True),
            'write_date': fields.datetime('Updated On', readonly=True),
            'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
            'getbase64enc' : fields.function(getbase64, method=True, string='Secure', type='char', size=500, readonly=True),
            
            'trip_id':fields.many2one('trip',"Trip")
    }
    
    _defaults = {
        'stage_id': 'new',
        'user_id': lambda s, cr, uid, c: uid,
        'color': 0,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'acesmanpowerevent', context=c),
    }
    _order = "id desc"
    
    def fetch_recruitment_trip(self,cr, uid, ids,context=None):
        '''
        This method will fetch recruitment trips data for the click from the dashboard of each user
        '''
        if context is None:
            context = {}
        print "-"*25
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        event_ids = property_ids = []
        log_in_user = property_user_id = False
        country_id = context['cid']
        
        # Find the log in user and his related property user id
        if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
            log_in_user = uid
            property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
            
        # Find property and related property ids of log in user with related to property user
        if log_in_user and property_user_id:
            property_id = manpower_user_obj.browse(cr,uid,property_user_id[0],context).property_id.id
            for obje in manpower_user_obj.browse(cr,uid,property_user_id,context):
                property_ids = [obj.id for obj in obje.property_ids]
            property_ids.append(property_id)
            print "property_id=",property_ids
                
        if len(property_ids):
            if len(property_ids) > 1:
                cr.execute("""SELECT DISTINCT(acesmanpowerevent_id) FROM acesmproperty_acesmevent_rel""" 
                           """ WHERE acesmanpowerproperty_id in %s"""%(tuple(property_ids),))
            else:
                cr.execute("""SELECT DISTINCT(acesmanpowerevent_id) FROM acesmproperty_acesmevent_rel"""
                           """ WHERE acesmanpowerproperty_id in (%s)"""%(tuple(property_ids)))
            rst = cr.fetchall()
            event_ids = [record[0] for record in rst if record[0] != None]
            
            domain = [('id','in',event_ids),('can_country_id','=',int(country_id))]
        else:
            domain = [('id','in',event_ids),('can_country_id','=',int(country_id))]
            
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if flag_grop_user or flag_group_admin or flag_group_consultant:     
            domain = [('can_country_id','=',int(country_id))]
            
        value = {
                'name': _('Recruitment Trips'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesmanpowerevent',
                'view_id': False,
                'domain': domain
                }
        return value
    
    def fetch_data(self, cr, uid, ids,context=None):
        '''
        This method will fetch data for the regular menu click of the user
        '''
        if context is None:
            context = {}
        print "-"*25
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        event_ids = property_ids = []
        log_in_user = property_user_id = False
        # Find the log in user and his related property user id
        if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
            log_in_user = uid
            property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
        # Find property and related property ids of log in user with related to property user
        if log_in_user and property_user_id:
            # Direct Property
            property_id = manpower_user_obj.browse(cr,uid,property_user_id[0],context).property_id.id
            # Other Properties
            for obje in manpower_user_obj.browse(cr,uid,property_user_id,context):
                property_ids = [obj.id for obj in obje.property_ids]
            property_ids.append(property_id)
            print "property_id=",property_ids
                
        if len(property_ids):
            if len(property_ids) > 1:
                cr.execute("""SELECT DISTINCT(acesmanpowerevent_id) FROM acesmproperty_acesmevent_rel""" 
                           """ WHERE acesmanpowerproperty_id in %s"""%(tuple(property_ids),))
            else:
                cr.execute("""SELECT DISTINCT(acesmanpowerevent_id) FROM acesmproperty_acesmevent_rel"""
                           """ WHERE acesmanpowerproperty_id in (%s)"""%(tuple(property_ids)))
            rst = cr.fetchall()
            event_ids = [record[0] for record in rst if record[0] != None]
            domain = [('id','in',event_ids)]
        else:
            domain = [('id','=',0)]
            
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if flag_grop_user or flag_group_admin or flag_group_consultant:     
            domain = []
            
        print "Domain=",domain
        value = {
                'name': _('Recruitment Trips'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesmanpowerevent',
                'view_id': False,
                'domain': domain
                }
        print "-"*25
        return value
    
class hr_job(osv.osv):
    _name = "hr.job"
    _inherit = "hr.job"
    _columns = {
        'acesmanpowerevent_ids': fields.many2many('acesmanpowerevent', 'hr_job_acesmanpowerevent_rel', 'hr_job_id', 'acesmanpowerevent_id'),
    }

class hr_employee(osv.osv):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
    }
    
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
    }

