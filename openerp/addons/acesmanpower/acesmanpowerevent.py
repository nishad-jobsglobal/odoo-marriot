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
import datetime
from datetime import datetime as dt
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT

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
    
    def action_view_screened(self,cr, uid, ids,context=None):
        active_id = ids[0]
        
        cr.execute("""SELECT DISTINCT(jobseeker_id) FROM acesevent_acesjobseeker_rel""" 
                           """ WHERE event_id=%s"""%(active_id))
        rst = cr.fetchall()
        candidates_ids = [record[0] for record in rst if record[0] != None]
        domain = [('id','in',candidates_ids)]
        value = {
                'name': _("Screened Candidates"),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesjobseeker',
                'view_id': False,
                'domain': domain
                }
        return value
    
    
    
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
    
    @api.multi
    def _get_manager_details(self):
        
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
                manpower_user_obj = self.env['acesmanpoweruser']
                property_obj = self.env['acesmanpowerproperty']
                manager = manpower_user_obj.search([('user_id','=',manager_id)])
                if manpower_user_obj.search([('user_id','=',self._uid)]):
                    property_user_id = manpower_user_obj.search([('user_id','=',self._uid)])
                    user_property_id = manpower_user_obj.browse([property_user_id.id]).property_id.id
                    manager_property_id = manpower_user_obj.browse([manager.id]).property_id.id
                    property_ids = property_obj.search([('id','child_of',manager_property_id)])
                    property_ids = [obj.id for obj in property_ids]
                    if user_property_id not in property_ids:
                        continue
                    else:
                        break
                    
        return manager or False
    
    @api.model
    def create(self,vals):
        
        new_id = super(acesmanpowerevent, self).create(vals)
        # Send SMS to the manager    
        initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
        if initiator_obj:
            manager = self._get_manager_details()
            manager_id = manager.user_id.id
            
            params = base64.b64encode(self._cr.dbname + '|' + str(new_id.id) + '|' + str(manager_id))
            link = "http://sm.jobsglobal.com/_wj/link.php?" + params
            print "Link",link
            to = manager.mobile or 0
            mess = 'A new Recruitment Trip has been proposed by ' + initiator_obj.name + '.  Follow URL link to take action, ' + link
        
            thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
            ames={}
            ames['msg'] = mess
            ames['gateway_id'] = 1
            ames['mobile'] = to
            ames['name'] = thelink + "to=" + to + "&" + 'text=' + mess
            created_id = self._uid or SUPERUSER_ID
            self.pool.get('sms.smsclient.queue').create(self._cr,created_id,ames)
        
        # Send Notification
        sysm = {}
        sysm['model'] = 'acesmanpowerevent'
        sysm['type'] = 'notification'
        sysm['subject'] = 'SMS'
        sysm['res_id'] = new_id.id
        sysm['body'] = 'Message has been sent'
        created_id = self._uid or SUPERUSER_ID
        self.pool.get('mail.message').create(self._cr,created_id,sysm)
        
        # Send mail to Manager to inform that a trip has been created and is waiting for approval.
        mail_server = None
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(self._cr, SUPERUSER_ID, [], order='sequence', limit=1)
        if mail_server_ids:
            mail_server = mail_server_obj.browse(self._cr, SUPERUSER_ID, mail_server_ids[0])
              
        if mail_server:
            body = subject = ''
            subject += "Recruitment Trip"
            url = (str('http://sm.jobsglobal.com/web')+
                         "?db=%s#id=%d&view_type=form&model=acesmanpowerevent"%(self._cr.dbname,new_id.id))
            body += 'A new Recruitment Trip has been proposed by ' + initiator_obj.name + '.  Follow URL link to take action, ' + url
                
            sender_obj = self.env['res.users'].search([('id','=',self._uid)])
            sender_email =  sender_obj.login
            manager_obj = self.env['res.users'].search([('id','=',manager_id)])
            manager_email = manager_obj.login or manager.email
            
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
            #partner_id = self.env['res.users'].browse([user_id]).partner_id.id
            partner_id = self.pool.get('res.users').browse(self._cr,SUPERUSER_ID,[user_id]).partner_id.id
            followers = {
                        'res_model':'trip',
                        'res_id':trip_id.id,
                        'partner_id':partner_id
                        }
            try:
                #self.env['mail.followers'].create(followers)
                self.pool.get('mail.followers').create(self._cr,SUPERUSER_ID,followers)
            except IntegrityError:
                continue
        return trip_id.id
    
    def send_notification_mail(self,initiator_obj):
        
        # Send SMS to the property by Group manager on Disapprove   
        #initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
        mobile = self.env['acesmanpowerevent'].search([('id','=',self.id)]).acesmanpoweruser_id.mobile
        trip_name = self.env['acesmanpowerevent'].search([('id','=',self.id)]).name

        to = mobile or 0
        mess = "Your request for the Recruitment Trip (" + trip_name + " ) has been denied "
        thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
        ames={}
        ames['msg'] = mess
        ames['gateway_id'] = 1
        ames['mobile'] = to
        ames['name'] = thelink + "to=" + to + "&" + 'text=' + mess
        self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
        
        # Send mail to property to inform that a trip has been cancelled/dispparoved.
        
        mail_server = None
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(self._cr, SUPERUSER_ID, [], order='sequence', limit=1)
        if mail_server_ids:
            mail_server = mail_server_obj.browse(self._cr, SUPERUSER_ID, mail_server_ids[0])
              
        if mail_server and initiator_obj:
            body = subject = ''
            subject += "Recruitment Trip"
            body += 'Your request for the Recruitment Trip has been denied by ' + initiator_obj.name
             
            manager_obj = self.env['res.users'].search([('id','=',initiator_obj.user_id.id)])
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
    def approve_trip(self):
        values = {}
        values['stage_id'] = self._context.get('stage_id')
        event_obj = self.env['acesmanpowerevent'].search([('id','=',self.id)])
        if event_obj.stage_id == 'approved':
            return
        event_obj.write(values)
    
    @api.multi
    def reject_trip(self):
        values = {}
        values['stage_id'] = self._context.get('stage_id')
        event_obj = self.env['acesmanpowerevent'].search([('id','=',self.id)])
        if event_obj.stage_id == 'disapproved':
            return
        event_obj.write(values)
        
    @api.multi
    def join_trip(self):
        event_obj = self.env['acesmanpowerevent'].search([('id','=',self.id)])
        # Find the log in user and his related property user id
        if self.env['acesmanpoweruser'].search([('user_id','=',self._uid)]):
            log_in_user = self._uid
            property_user_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
        if log_in_user and property_user_obj:
            property_id = self.env['acesmanpoweruser'].browse(property_user_obj.id).property_id.id
            
        if property_id:
            values = {}
            values['stage_id'] = self._context.get('stage_id')
            write_uid = self._uid
            values = {}
            self._cr.execute("SELECT acesmanpowerproperty_id FROM acesmproperty_acesmevent_rel WHERE acesmanpowerevent_id=%s AND acesmanpowerproperty_id=%s"%(str(self.id),property_id))
            property_ids = self._cr.fetchone()
            if property_ids not in (None,[None],[]):
                pass
            else:
                values['acesmanpowerproperty_ids'] = [(4,property_id)]
                values['write_uid'] = int(write_uid)
                values['stage_id'] = 'joined'
            event_obj.write(values)

    def update_trip(self,cr, uid, values,context=None):
        print "Val",values
        val = base64.b64decode(values)
        val = val.split('|')
        status = val[0] or ''    # Status - modified/approved/disapproved/joined
        database = val[1] or ''  # Database - DB on which it running
        ids = int(val[2])        # Record ID - Recruitment Trip ID 

        event_obj = self.pool.get('acesmanpowerevent').browse(cr,uid,ids,context)
        if status == 'modified':
            #modified|demo|103|178|2016-05-02|2016-05-13|177
            loc_id = val[3]
            write_uid = val[6]
            date_start = datetime.datetime.strptime(val[4], '%Y-%m-%d')
            date_end = datetime.datetime.strptime(val[5], '%Y-%m-%d')
            date_start = dt.strftime(date_start, '%Y-%m-%d')
            date_end = dt.strftime(date_end, '%Y-%m-%d')
            values = {}
            values['can_country_id'] = loc_id
            values['datestart'] = date_start
            values['dateend'] = date_end
            values['write_uid'] = int(write_uid)
            values['stage_id'] = 'modified'
        elif status == 'disapproved':
            write_uid = val[3]
            values = {}
            values['stage_id'] = 'disapproved'
            values['write_uid'] = int(write_uid)
        elif status == 'approved':
            write_uid = val[3]
            values = {}
            values['stage_id'] = 'approved'
            values['write_uid'] = int(write_uid)
        elif status == 'joined':
            property_id = int(val[3])
            write_uid = val[4]
            values = {}
            cr.execute("SELECT acesmanpowerproperty_id FROM acesmproperty_acesmevent_rel WHERE acesmanpowerevent_id=%s AND acesmanpowerproperty_id=%s"%(str(ids),property_id))
            property_ids = cr.fetchone()
            if property_ids not in (None,[None],[]):
                pass
            else:
                values['acesmanpowerproperty_ids'] = [(4,property_id)]
            values['write_uid'] = int(write_uid)
            values['stage_id'] = 'joined'
            print "Values",values
        event_obj.write(values)
    
    @api.multi
    def write(self, values):
        stage_id = values.get('stage_id',False)
        write_uid = values.get('write_uid',False)
        event_obj = self.env['acesmanpowerevent'].search([('id','=',self.id)])
        print "EVENT--",event_obj,write_uid,self.id
        
        # Validations for the event 
        flag_group_admin = self.env['res.users'].has_group('base.group_marriot_group_property_admin')
        if not flag_group_admin:
            if stage_id == 'joined':
                pass
            else:
                if stage_id != 'new' and stage_id != False:
                    raise osv.except_osv(_('Warning!'), _("You don't have the permission to change the stage of this trip. Please contact Group Manager"))
                elif stage_id == False and len(values) >= 1:
                    if event_obj.stage_id != 'new':
                        raise osv.except_osv(_('Warning!'), _("You don't have the permission to change the details of this trip." 
                                                      " Please contact Group Manager"))
                elif stage_id == 'new':
                    if event_obj.stage_id != 'new':
                        raise osv.except_osv(_('Warning!'), _("You don't have the permission to change the stage of this trip. Please contact Group Manager"))
        if flag_group_admin:
            # Find out if a trip is already created with respect to this event.
            marriot_trip_id = self.env['trip'].search([('marriot_trip_id','=',self.id)])
        else:
            marriot_trip_id = None
        mail_server = None
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(self._cr, SUPERUSER_ID, [], order='sequence', limit=1)
        if mail_server_ids:
            mail_server = mail_server_obj.browse(self._cr, SUPERUSER_ID, mail_server_ids[0])

        # Send SMS & Mail to all properties to inform an Event has been approved and if wish then join with them.
        if stage_id == 'approved':
            
            property_ids = properties = []
            numproperty = 0
            msg_body = ''
            
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
                    manpower_user_obj = self.env['acesmanpoweruser']
                    property_obj = self.env['acesmanpowerproperty']
                    manager = manpower_user_obj.search([('user_id','=',manager_id)])
                    initiator_obj = False
                    if write_uid:
                        initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',int(write_uid))])
                        #self._uid = int(write_uid)
                    else:
                        initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
                    if initiator_obj:
                        if write_uid:
                            property_user_id = manpower_user_obj.search([('user_id','=',int(write_uid))])
                            #self._uid = int(write_uid)
                        else:
                            property_user_id = manpower_user_obj.search([('user_id','=',self._uid)])
                        user_property_id = manpower_user_obj.browse([property_user_id.id]).property_id.id
                        manager_property_id = manpower_user_obj.browse([manager.id]).property_id.id
                        property_ids = property_obj.search([('id','child_of',manager_property_id)])
                        property_ids = [obj.id for obj in property_ids]
                        if user_property_id not in property_ids:
                            continue
                        else:
                            properties = self.env['acesmanpowerproperty'].search([['mobile', '!=', ''],['id', 'in', property_ids]])
                            break

            if len(properties):
                for property_obj in properties:
                    thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
                    
                    flag = True
                    # weather to send joining link to all users or to a responsible user alone.
                    if not flag:
                        manpower_user_obj = self.env['acesmanpoweruser'].search(['property_id','=',property_obj.id])
                        for manpower_user in manpower_user_obj:
                            
                            params = base64.b64encode(self._cr.dbname +  '|' + str(self.id) + '|' + str(property_obj.id) + '|' + str(manpower_user.id))
                            
                            link = "http://sm.jobsglobal.com/_wj/join.php?" + params
                            
                            mess = 'Recruitment Trip,' + self.name + ' , has been approved. Follow URL link to take action, ' + link
                            ames={}
                            ames['msg'] = mess
                            ames['gateway_id'] = 2
                            ames['mobile'] = manpower_user.mobile
                            ames['name'] = thelink + "to=" + manpower_user.mobile + "&" + 'text=' + mess
                            self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
                            numproperty += 1
                            
                            msg_body = 'Invitations has been sent to ' + str(numproperty) + ' property members'
                            
                            initiator_obj = False
                            if write_uid:
                                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',int(write_uid))])
                                #self._uid = int(write_uid)
                            else:
                                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
                            
                            if mail_server and initiator_obj:
                                body = subject = ''
                                subject += "Recruitment Trip"
                                url = (str('http://sm.jobsglobal.com/web')+
                                             "?db=%s#id=%d&view_type=form&model=acesmanpowerevent"%(self._cr.dbname,event_obj.id))
                                body += 'A new Recruitment Trip,'+ self.name +' has been approved by ' + initiator_obj.name + '.  Follow URL link to take action, ' + url
                                if write_uid:
                                    manager_obj = self.env['res.users'].search([('id','=',int(write_uid))])
                                    #self._uid = int(write_uid)
                                else:
                                    manager_obj = self.env['res.users'].search([('id','=',self._uid)])
                                
                                manager_mail =  manager_obj.login
                                receiver_email =  manpower_user.email
                                
                                if manager_mail and receiver_email:
                                    try:
                                        msg = mail_server_obj.build_email(
                                                                        email_from = manager_mail,
                                                                        email_to = [receiver_email],
                                                                        subject = subject,
                                                                        body = body,
                                                                        subtype_alternative = 'plain')
                                        res = mail_server_obj.send_email(self._cr, self._uid, msg,
                                           mail_server_id=mail_server_ids[0])
                                    except Exception:
                                        return True
                            
                    else:
                        params = base64.b64encode(self._cr.dbname + '|' + str(self.id) + '|' + str(property_obj.id) + '|' + str(property_obj.acesmanpoweruser_id.user_id.id))
                        link = "http://sm.jobsglobal.com/_wj/join.php?" + params
                        print "Link2",link
                        mess = 'Recruitment Trip,' + self.name + '  has been approved. Follow URL link to take action, ' + link
                        ames={}
                        ames['msg'] = mess
                        ames['gateway_id'] = 2
                        ames['mobile'] = property_obj.mobile
                        ames['name'] = thelink + "to=" + property_obj.mobile + "&" + 'text=' + mess
                        self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
                        numproperty += 1
                        
                        msg_body = 'Invitations has been sent to ' + str(numproperty) + ' properties'
                        initiator_obj = False
                        if write_uid:
                            initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',int(write_uid))])
                        else:
                            initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
                        
                        if mail_server and initiator_obj:
                            body = subject = ''
                            subject += "Recruitment Trip"
                            url = (str('http://sm.jobsglobal.com/web')+
                                         "?db=%s#id=%d&view_type=form&model=acesmanpowerevent"%(self._cr.dbname,event_obj.id))
                            body += 'A new Recruitment Trip,'+ self.name +' has been approved by ' + initiator_obj.name + '.  Follow URL link to take action, ' + url
                            if write_uid:
                                manager_obj = self.env['res.users'].search([('id','=',int(write_uid))])
                            else:
                                manager_obj = self.env['res.users'].search([('id','=',self._uid)])
                            manager_mail =  manager_obj.login
                            rceiver_email =  property_obj.email
                            
                            if manager_mail and rceiver_email:
                                try:
                                    msg = mail_server_obj.build_email(
                                                                    email_from = manager_mail,
                                                                    email_to = [rceiver_email],
                                                                    subject = subject,
                                                                    body = body,
                                                                    subtype_alternative = 'plain')
                                    res = mail_server_obj.send_email(self._cr, self._uid, msg,
                                       mail_server_id=mail_server_ids[0])
                                except Exception:
                                    return True
                
                # Record mail_message in respective event.
                sysm = {}
                sysm['model'] = 'acesmanpowerevent'
                sysm['type'] = 'notification'
                sysm['subject'] = 'SMS'
                sysm['res_id'] = self.id
                sysm['body'] = msg_body or ''
                updated_user_id = int(write_uid) or self._uid or SUPERUSER_ID
                self.pool.get('mail.message').create(self._cr,updated_user_id,sysm)
                
        if stage_id == 'joined':
            manager = self._get_manager_details()
            manager_id = manager.user_id.id
            initiator_obj = False
            if write_uid:
                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',int(write_uid))])
                initiator_name = initiator_obj.name 
            else:
                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
                
            if manager_id:
                manager_obj = self.env['acesmanpoweruser'].search([('user_id','=',int(manager_id))])
            
            thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
            mess = initiator_name + ' would like to join the trip ' + self.name
            ames={}
            ames['msg'] = mess
            ames['gateway_id'] = 2
            ames['mobile'] = manager_obj.mobile or 0
            ames['name'] = thelink + "to=" + manager_obj.mobile + "&" + 'text=' + mess
            self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
            
            if mail_server:
                body = subject = ''
                subject += "Recruitment Trip"
                url = (str('http://sm.jobsglobal.com/web')+
                             "?db=%s#id=%d&view_type=form&model=acesmanpowerevent"%(self._cr.dbname,event_obj.id))
                body += initiator_name + ' would like to join the trip ' + self.name + url
                
                if write_uid:
                    initiator_obj = self.env['res.users'].search([('id','=',int(write_uid))])
                else:
                    initiator_obj = self.env['res.users'].search([('id','=',self._uid)])
                initiator_email =  initiator_obj.login
                manager_email =  manager_obj.email
                
                if manager_email and initiator_email:
                    try:
                        msg = mail_server_obj.build_email(
                                                        email_from = initiator_email,
                                                        email_to = [manager_email],
                                                        subject = subject,
                                                        body = body,
                                                        subtype_alternative = 'plain')
                        res = mail_server_obj.send_email(self._cr, self._uid, msg,
                           mail_server_id=mail_server_ids[0])
                    except Exception:
                        return True
        if stage_id == 'modified':
            
            mobile_no = self.env['acesmanpowerevent'].search([('id','=',self.id)]).acesmanpoweruser_id.mobile
            initiator_obj = False
            if write_uid:
                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',int(write_uid))])
                initiator_name = initiator_obj.name 
            else:
                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
            country_name = self.env['res.country'].search([('id','=',values['can_country_id'])]).name
            
            thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
            mess = 'Your request for the trip ' + self.name + ' has modified, view details: ' +\
                    'Recruit Location: ' + country_name + ', Start Date: '+ values['datestart'] +\
                    ', End Date: '+ values['dateend']
            ames={}
            ames['msg'] = mess
            ames['gateway_id'] = 2
            ames['mobile'] = mobile_no or 0
            ames['name'] = thelink + "to=" + mobile_no + "&" + 'text=' + mess
            self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
        
        # Create a Trip in Human Resource -> Recruitment Trips -> Trips to do further follow ups.
        if not marriot_trip_id and stage_id == 'approved':
            trip_id = self.create_trip()
            values.update({'trip_id':trip_id})
            job_ids = [obj.id for obj in event_obj.acesmanpowerjob_ids]
            for jobs in self.env['acesmanpowerjob'].browse(job_ids):
                jobs.write({'stage':'approve'})
        elif not marriot_trip_id and stage_id in ('disapproved','cancelled'):
            initiator_obj = False
            if write_uid:
                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',int(write_uid))])
            else:
                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
            self.send_notification_mail(initiator_obj)
            job_ids = [obj.id for obj in event_obj.acesmanpowerjob_ids]
            for jobs in self.env['acesmanpowerjob'].browse(job_ids):
                jobs.write({'stage':'reject'})
        elif marriot_trip_id and stage_id == 'done':
            job_ids = [obj.id for obj in event_obj.acesmanpowerjob_ids]
            for jobs in self.env['acesmanpowerjob'].browse(job_ids):
                jobs.write({'stage':'done'})
        elif not marriot_trip_id and stage_id == 'new':
            job_ids = [obj.id for obj in event_obj.acesmanpowerjob_ids]
            for jobs in self.env['acesmanpowerjob'].browse(job_ids):
                jobs.write({'stage':'new'})
        else:
            if values.get('stage_id',False) in ('joined','modified'):
                values.pop('stage_id')
            values = values
        print "values-------",values
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
            
            'datestart': fields.date(string='Start',),
            'dateend': fields.date(string='End', ),
            
            'twitterhashtag': fields.char(size=100, string='Twitter Hash Tag', ),
            'color': fields.integer('Color Index'),
            'url_image': fields.char(size=500, string='Image url', ),
            'description': fields.text(string='Notes', ),
            
            'hr_job_ids': fields.many2many('hr.job','hr_job_acesmanpowerevent_rel', 'acesmanpowerevent_id', 'hr_job_id'),
            'acesmanpowerjob_ids': fields.one2many('acesmanpowerjob','acesmanpowerevent_id','Jobs'),
            'acesmanpowerproperty_ids': fields.many2many('acesmanpowerproperty','acesmproperty_acesmevent_rel', 'acesmanpowerevent_id', 'acesmanpowerproperty_id', string="Properties"),
            
            'jobseeker_ids': fields.many2many('acesjobseeker','acesevent_acesjobseeker_rel', 'event_id', 'jobseeker_id', string="Candidates",readonly=True),
            
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
        property_obj = self.pool.get('acesmanpowerproperty')
        event_ids = event_ids1 = property_ids = []
        log_in_user = property_user_id = property_id = False
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
            #print "property_id=",property_ids

        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if (flag_grop_user or flag_group_admin) and property_id:
            all_child_ids = property_obj.search(cr,uid,[('id','child_of',[property_id])],context=context)
            if all_child_ids:
                property_ids.extend(all_child_ids)
                property_ids = list(set(property_ids))
                
        if len(property_ids):
            if len(property_ids) > 1:
                cr.execute("""SELECT DISTINCT(acesmanpowerevent_id) FROM acesmproperty_acesmevent_rel""" 
                           """ WHERE acesmanpowerproperty_id in %s"""%(tuple(property_ids),))
            else:
                cr.execute("""SELECT DISTINCT(acesmanpowerevent_id) FROM acesmproperty_acesmevent_rel"""
                           """ WHERE acesmanpowerproperty_id in (%s)"""%(tuple(property_ids)))
            rst = cr.fetchall()
            event_ids = [record[0] for record in rst if record[0] != None] 
            event_obj = self.pool.get('acesmanpowerevent')
            event_ids1 = event_obj.search(cr,uid,[('acesmanpoweruser_id','=',property_user_id[0])])
            if event_ids or event_ids1:
                event_ids.extend(event_ids1)
                event_ids = list(set(event_ids)) 
            domain = [('id','in',event_ids),('can_country_id','=',int(country_id))]
        else:
            domain = [('id','in',event_ids),('can_country_id','=',int(country_id))]
       
        if flag_group_admin:
            all_user_ids = manpower_user_obj.search(cr,uid,[('property_id','in',property_ids)])
            event_ids = event_obj.search(cr,uid,[('acesmanpoweruser_id','in',all_user_ids)])
            domain = [('id','in',event_ids),('can_country_id','=',int(country_id))]  
        if flag_group_consultant:     
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
        property_obj = self.pool.get('acesmanpowerproperty')
        event_obj = self.pool.get('acesmanpowerevent')
        event_ids = event_ids1 = property_ids = []
        log_in_user = property_user_id = property_id = False
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
            #print "property_id=",property_ids
            
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if (flag_grop_user or flag_group_admin) and property_id:
            all_child_ids = property_obj.search(cr,uid,[('id','child_of',[property_id])],context=context)
            if all_child_ids:
                property_ids.extend(all_child_ids)
                property_ids = list(set(property_ids))
                
        if len(property_ids):
            if len(property_ids) > 1:
                cr.execute("""SELECT DISTINCT(acesmanpowerevent_id) FROM acesmproperty_acesmevent_rel""" 
                           """ WHERE acesmanpowerproperty_id in %s"""%(tuple(property_ids),))
            else:
                cr.execute("""SELECT DISTINCT(acesmanpowerevent_id) FROM acesmproperty_acesmevent_rel"""
                           """ WHERE acesmanpowerproperty_id in (%s)"""%(tuple(property_ids)))
            rst = cr.fetchall()
            event_ids = [record[0] for record in rst if record[0] != None]
            event_obj = self.pool.get('acesmanpowerevent')
            event_ids1 = event_obj.search(cr,uid,[('acesmanpoweruser_id','=',property_user_id[0])])
            if event_ids or event_ids1:
                event_ids.extend(event_ids1)
                event_ids = list(set(event_ids))               
            domain = [('id','in',event_ids)]
        else:
            domain = [('id','=',0)]

        if flag_group_admin:
            all_user_ids = manpower_user_obj.search(cr,uid,[('property_id','in',property_ids)])
            event_ids = event_obj.search(cr,uid,[('acesmanpoweruser_id','in',all_user_ids)])
            domain = [('id','in',event_ids)]
        
        if flag_group_consultant:     
            domain = []
            
        print "Trip Domain=",domain
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

