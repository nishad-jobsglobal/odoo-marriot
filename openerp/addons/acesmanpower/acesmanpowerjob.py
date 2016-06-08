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
import urllib
import base64

from openerp import api
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

class acesmanpowerjob(osv.osv):
    _name = 'acesmanpowerjob'
    _description = "Job"
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _get_default_property(self,cr,uid,context=None):
        res = []
        login_user = self.pool.get('acesmanpoweruser').search(cr,uid,[('user_id','=',uid)])
        for user in self.pool.get('acesmanpoweruser').browse(cr, uid, login_user, context=context):
            if user.property_id:
                res.append(user.property_id.id)
        if len(res):
            return res[0]
        else:
            return res

    _columns = {
        'name': fields.char(size=256, string='Job Title', required=True),
        'quantity': fields.integer('No. of Vacancies'),
        'jobdescription': fields.text(string='Job Description', ),
        'qualification': fields.text(string='Qualifications', ),
        
        'stage': fields.selection([('new', 'New'),('approve', 'Approved'),('reject','Rejected'),('done','Done')],'Status'),
        'user_id': fields.many2one('res.users', 'Created by', readonly=True),
        'acesmanpoweruser_id': fields.related('user_id', 'acesmanpoweruser_id', type="many2one", relation="acesmanpoweruser", string="Recruitment User", store=True),
        #'acesmanpoweruser_id': fields.many2one('acesmanpoweruser', 'Owner', track_visibility='onchange'),
        'acesmanpowerproperty_id': fields.many2one('acesmanpowerproperty', 'Property',required=True),
        
        #'acesmanpowerproperty_id': fields.related('acesmanpoweruser_id', 'acesmanpowerproperty_id', type="many2one", relation="acesmanpowerproperty", string="Property", store=True),
        'acesmanpowerevent_id': fields.many2one('acesmanpowerevent', 'Recruitment Event'),
        
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated On', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
    }
    
    _defaults = {
        'stage' : 'new',
        'user_id': lambda s, cr, uid, c: uid,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'acesmanpowerjob', context=c),
        'acesmanpoweruser_id': lambda self, cr, uid, c: c.get('acesmanpoweruser_id', False),
        'acesmanpowerproperty_id':lambda s, cr, uid, c: s._get_default_property(cr, uid,context=c)
    }
    
    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.stage != 'new':
                raise osv.except_osv(_('Warning!'),_('You can only delete draft records!'))
        return super(acesmanpowerjob, self).unlink(cr, uid, ids, context)
    
    def _get_manager_details(self,cr,uid,context=None):
        # Send SMS to the Property Group Manager for the approval of a trip. 
        cr.execute("SELECT id FROM res_groups WHERE name='Group Management'")
        group_id = cr.fetchone()[0]
        cr.execute("SELECT uid FROM res_groups_users_rel WHERE gid="+str(group_id))
        rst = cr.fetchall()
        if rst not in (None,[None],[]):
            for record in rst:
                if record[0] == 1:
                    continue
                manager_id = record[0]
                manpower_user_obj = self.pool.get('acesmanpoweruser')
                property_obj = self.pool.get('acesmanpowerproperty')
                manager = manpower_user_obj.search(cr,uid,[('user_id','=',manager_id)])
                if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
                    property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
                    user_property_id = manpower_user_obj.browse(cr,uid,[property_user_id[0]]).property_id.id
                    manager_property_id = manpower_user_obj.browse(cr,uid,[manager[0]]).property_id.id
                    property_ids = property_obj.search(cr,uid,[('id','child_of',manager_property_id)])
                    
                    #print "UID-UPID-PID",uid,property_user_id,user_property_id
                    #print "MID-MPID-PID",manager_id,manager,manager_property_id
                    print "All PIDS",property_ids
                    if user_property_id not in property_ids:
                        continue
                    else:
                        break
                else:
                    continue
        return manager_id or False

    def propose_job(self,cr,uid,values,context=None):
        
        print "----------"
        print "values",values
        propose_vals = {}
        new_job_ids = [] 
        
        eid = int(values['eid'])
        pid = int(values['pid'])
        write_uid = int(values['uid'])
        
        propose_vals['acesmanpowerevent_id'] = eid
        propose_vals['acesmanpowerproperty_id'] = pid
        propose_vals['write_uid'] = write_uid
        initiator_obj = False
        if write_uid:
            initiator_obj = self.pool.get('acesmanpoweruser').search(cr,uid,[('user_id','=',int(write_uid))])
            #self.sudo(int(write_uid))
            propose_vals['create_uid'] = write_uid
            propose_vals['user_id'] = write_uid
            propose_vals['acesmanpoweruser_id'] = initiator_obj[0]
            #TO DO
            # Get company ID of the logined user
        else:
            initiator_obj = self.pool.get('acesmanpoweruser').search(cr,uid,[('user_id','=',uid)])
            propose_vals['create_uid'] = uid
            propose_vals['user_id'] = uid
            propose_vals['acesmanpoweruser_id'] = initiator_obj[0]
        
        if len(values['jobs']) > 1:
            jobs = values['jobs'] 
            for job in jobs:
                propose_vals['name'] = job[0] # title
                propose_vals['quantity'] = job[1] # quantity
                new_id = super(acesmanpowerjob, self).create(cr,write_uid,propose_vals)
                new_job_ids.append(new_id)
        else:
            propose_vals['name'] = values['jobs'][0][0]
            propose_vals['quantity'] = values['jobs'][0][1]
            
            new_id = super(acesmanpowerjob, self).create(cr,write_uid,propose_vals)
            new_job_ids.append(new_id)
            
        if initiator_obj:
            initiator_name = self.pool.get('acesmanpoweruser').browse(cr,uid,initiator_obj[0],context).name
            manager_id = self._get_manager_details(cr,write_uid,context=None)
            if not manager_id:
                return
            jid = ','.join([str(x) for x in new_job_ids])
            params = base64.b64encode(cr.dbname + '|' + str(eid) + '|' + str(pid) +'|' + str(jid) + '|' + str(manager_id))
            link = "http://sm.jobsglobal.com/_wj/viewjobs.php?" + params
            
            manpower_user_obj = self.pool.get('acesmanpoweruser')
            manager = manpower_user_obj.search(cr,uid,[('user_id','=',manager_id)])
            manager = manpower_user_obj.browse(cr,uid,manager[0],context)

            to = manager.mobile or 0
            mess = 'New open positions has been proposed by ' + initiator_name + '.  Follow URL link to take action, ' + link
            thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
            ames={}
            ames['msg'] = mess
            ames['gateway_id'] = 1
            ames['mobile'] = to
            ames['name'] = thelink + "to=" + to + "&" + 'text=' + mess
            created_id = uid or SUPERUSER_ID
            self.pool.get('sms.smsclient.queue').create(cr,created_id,ames)

    def update_job(self,cr, uid, values,context=None):
        acesmanpowerjob_obj = self.pool.get('acesmanpowerjob')
        status = values['status'] # Status -   approved/reject/modified
        write_uid = int(values['uid'])
        if status in ('approve','reject'):
            if len(values['jobs']) > 1:
                jobs = values['jobs']
                for job in jobs:
                    values = {}
                    jid = int(job) # ID of Job
                    values['stage'] = status
                    values['write_uid'] = write_uid
                    job_obj = acesmanpowerjob_obj.browse(cr,uid,jid,context)
                    job_obj.write(values)
            else:
                jobs = values['jobs']
                values = {}
                values['stage'] = status
                values['write_uid'] = write_uid
                jid = int(jobs[0])
                job_obj = acesmanpowerjob_obj.browse(cr,uid,jid,context)
                job_obj.write(values)
        elif status == 'modified':
            jobs = values['jobs']
            values = {}
            values['name'] = jobs[1]
            values['quantity'] = int(jobs[2])
            jid = int(jobs[0]) # ID of Job
            job_obj = acesmanpowerjob_obj.browse(cr,uid,jid,context)
            job_obj.write(values)
  
    @api.model
    def create(self,vals):
        
        new_id = super(acesmanpowerjob, self).create(vals)
        
        job_obj = self.env['acesmanpowerjob'].search([('id', '=', new_id.id)])
        event_id = job_obj.acesmanpowerevent_id.id
        property_id = job_obj.acesmanpowerproperty_id.id
        event_job_user_id = job_obj.acesmanpowerevent_id.user_id.id
        manager_id = False
        
        # Add new jobs with property with which it is associated
        if property_id:
            job_vals = {}
            prop_obj = self.env['acesmanpowerproperty'].search([('id','=',property_id)])
            job_vals['jobs_ids'] = [(4,new_id.id)]
            prop_obj.write(job_vals)
        
        if event_job_user_id != self._uid:
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
          
            # Send SMS to the manager    
            initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
            if initiator_obj:
                params = base64.b64encode(self._cr.dbname + '|' + str(event_id) + '|' + str(property_id) +'|' + str(new_id.id) + '|' + str(manager_id))
                link = "http://sm.jobsglobal.com/_wj/viewjobs.php?" + params
                print "Link",link

                manpower_user_obj = self.env['acesmanpoweruser']
                if manager_id:
                    manager = manpower_user_obj.search([('user_id','=',manager_id)])
    
                    to = manager.mobile or 0
                    mess = 'A new Job position has been proposed by ' + initiator_obj.name + '.  Follow URL link to take action, ' + link
                
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
            sysm['model'] = 'acesmanpowerjob'
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
                  
            if mail_server and initiator_obj:
                body = subject = ''
                subject += "Open Position"
                url = (str('http://sm.jobsglobal.com/web')+
                             "?db=%s#id=%d&view_type=form&model=acesmanpowerjob"%(self._cr.dbname,new_id.id))
                body += 'A new Open position has been proposed by ' + initiator_obj.name + '.  Follow URL link to take action, ' + url
                    
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
                        return True
        return new_id
    
    @api.multi
    def write(self,values):
        stage_id = values.get('stage',False)
        write_uid = values.get('write_uid',False)
        job_obj = self.env['acesmanpowerjob'].search([('id', '=', self.id)])
        # Get the mail server details
        mail_server = None
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(self._cr, SUPERUSER_ID, [], order='sequence', limit=1)
        if mail_server_ids:
            mail_server = mail_server_obj.browse(self._cr, SUPERUSER_ID, mail_server_ids[0])

        # Update the job details in property
        current_property_id = values.get('acesmanpowerproperty_id',False)
        existing_property_id = job_obj.acesmanpowerproperty_id.id or False
        prop_vals = prop_vals2 = {}
        
        if current_property_id and (not existing_property_id):
            property_obj = self.env['acesmanpowerproperty'].search([('id','=',current_property_id)])
            prop_vals['jobs_ids'] = [(4,job_obj.id)]
            property_obj.write(prop_vals)
        elif current_property_id and existing_property_id:
            if existing_property_id != current_property_id:
                # Delete existing job seeker from Trip
                property_obj1 = self.env['acesmanpowerproperty'].search([('id','=',existing_property_id)])
                prop_vals['jobs_ids'] = [(3,job_obj.id)]
                property_obj1.write(prop_vals)
                # Add job seeker to the new trip
                property_obj2 = self.env['acesmanpowerproperty'].search([('id','=',current_property_id)])
                prop_vals2['jobs_ids'] = [(4,job_obj.id)]
                property_obj2.write(prop_vals2)
        
        if stage_id == 'reject':
	    initiator_obj = False
            if write_uid:
                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',int(write_uid))])
            else:
                initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
            self.send_notification_mail(initiator_obj)
        
        if stage_id == 'approve':
            job_obj = self.env['acesmanpowerjob'].search([('id', '=', self.id)])
            mobile = self.env['acesmanpowerjob'].search([('id','=',self.id)]).acesmanpoweruser_id.mobile
            
            thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
	    mess = 'Your request for the Open position ' + self.name + '  has been approved'
            ames={}
            ames['msg'] = mess
            ames['gateway_id'] = 2
            ames['mobile'] = mobile
            ames['name'] = thelink + "to=" + mobile + "&" + 'text=' + mess
            self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
	    manager_obj = False
            if write_uid:
                manager_obj = self.env['acesmanpoweruser'].search([('user_id','=',int(write_uid))])
            else:
                manager_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
            
            if mail_server and manager_obj:
                body = subject = ''
                subject += "Open Position"
                url = (str('http://sm.jobsglobal.com/web')+
                             "?db=%s#id=%d&view_type=form&model=acesmanpowerjob"%(self._cr.dbname,job_obj.id))
                body += 'A new Open Position,'+ self.name +' has been approved by ' + manager_obj.name + '.  Follow URL link to view, ' + url
		if write_uid:
                    manager_obj = self.env['res.users'].search([('id','=',int(write_uid))])
                    #self._uid = int(write_uid)
                else:
                    manager_obj = self.env['res.users'].search([('id','=',self._uid)])
                manager_mail =  manager_obj.login
                
                acesmanpoweruser_id = self.env['acesmanpowerjob'].search([('id','=',self.id)]).acesmanpoweruser_id.id
                receiver_obj = self.env['res.users'].search([('acesmanpoweruser_id','=',acesmanpoweruser_id)])
                receiver_email =  receiver_obj.login
                
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
                
            # Record mail_message in respective event.
#             sysm = {}
#             sysm['model'] = 'acesmanpowerjob'
#             sysm['type'] = 'notification'
#             sysm['subject'] = 'SMS'
#             sysm['res_id'] = self.id
#             sysm['body'] = 'Invitations has been sent to job initiator'  
#             self.pool.get('mail.message').create(self._cr,SUPERUSER_ID,sysm)
        
        return super(acesmanpowerjob, self).write(values)
    
    def send_notification_mail(self,initiator_obj):
        
        # Send SMS to the manager    
        #manager_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)]) # Manager
        mobile = self.env['acesmanpowerjob'].search([('id','=',self.id)]).acesmanpoweruser_id.mobile

        to = mobile or 0
        mess = 'Your request for the Open position has been denied.'
        thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
        ames={}
        ames['msg'] = mess
        ames['gateway_id'] = 2
        ames['mobile'] = to
        ames['name'] = thelink + "to=" + to + "&" + 'text=' + mess
        self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
        
        # Send mail to Manager to inform that a trip has been created and is waiting for approval.
        
        mail_server = None
        mail_server_obj = self.pool.get('ir.mail_server')
        mail_server_ids = mail_server_obj.search(self._cr, SUPERUSER_ID, [], order='sequence', limit=1)
        if mail_server_ids:
            mail_server = mail_server_obj.browse(self._cr, SUPERUSER_ID, mail_server_ids[0])
              
        if mail_server and initiator_obj:
            body = subject = ''
            subject += "Open Position"
            body += 'Your request for the Open Position has been denied by ' + initiator_obj.name
	    manager_obj = self.env['res.users'].search([('id','=',initiator_obj.user_id.id)])
            manager_email = manager_obj.login
            
            acesmanpoweruser_id = self.env['acesmanpowerjob'].search([('id','=',self.id)]).acesmanpoweruser_id.id
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
    
    
    def fetch_data(self, cr, uid, ids,context=None):
        if context is None:
            context = {}
        print "-"*25
        
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        jobposition_obj = self.pool.get('acesmanpowerjob')
        property_obj = self.pool.get('acesmanpowerproperty')
        jobposition_ids = property_ids = []
        log_in_user = property_user_id = property_id = False
        # Find the log in user and his related property user id
        
        if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
            log_in_user = uid
            property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
            #print "Log In user {'%s'} = Property User {'%s'}"%(log_in_user,property_user_id[0])
        
        # Find property and related property ids of log in user with related to property user
        if log_in_user and property_user_id:
            # Direct Property
            property_id = manpower_user_obj.browse(cr,uid,property_user_id[0],context).property_id.id
            # Other Properties
            for obje in manpower_user_obj.browse(cr,uid,property_user_id,context):
                property_ids = [obj.id for obj in obje.property_ids]
            property_ids.append(property_id)
            #print "property_id=",property_id,property_ids
        
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if (flag_grop_user or flag_group_admin) and property_id:
            all_child_ids = property_obj.search(cr,uid,[('id','child_of',[property_id])],context=context)
            if all_child_ids:
                property_ids.extend(all_child_ids)
                property_ids = list(set(property_ids))
                
        # Find all the job positions which is linked with any of the property
        if property_ids:
            jobposition_ids = jobposition_obj.search(cr,uid,[('acesmanpowerproperty_id','in',list(set(property_ids)))],context=context)
            #print "jobposition_ids=",jobposition_ids
                
        domain = [('id','in',jobposition_ids)]
            
        if flag_group_consultant:     
            domain = []
        
        print "Job Domain=",domain
        
        value = {
                'name': _('Open Positions'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesmanpowerjob',
                'view_id': False,
                'domain': domain
                }
        
        print "-"*25
        
        return value