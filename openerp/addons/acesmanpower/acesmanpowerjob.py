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
from openerp import api
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _

class acesmanpowerjob(osv.osv):
    _name = 'acesmanpowerjob'
    _description = "Job"
    _order = "name asc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'name': fields.char(size=256, string='Job Title', required=True),
        'quantity': fields.integer('Quantity'),
        'jobdescription': fields.text(string='Job Description', ),
        'qualification': fields.text(string='Qualifications', ),
        
        'stage': fields.selection([('new', 'New'),('approve', 'Approved'),('reject','Rejected'),('done','Done')]),
        'user_id': fields.many2one('res.users', 'Created by', readonly=True),
        'acesmanpoweruser_id': fields.related('user_id', 'acesmanpoweruser_id', type="many2one", relation="acesmanpoweruser", string="Recruitment User", store=True),
        #'acesmanpoweruser_id': fields.many2one('acesmanpoweruser', 'Owner', track_visibility='onchange'),
        'acesmanpowerproperty_id': fields.many2one('acesmanpowerproperty', 'Property',required=True),
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
    }
    
    def unlink(self, cr, uid, ids, context=None):
        for rec in self.browse(cr, uid, ids, context=context):
            if rec.stage != 'new':
                raise osv.except_osv(_('Warning!'),_('You can only delete draft records!'))
        return super(acesmanpowerjob, self).unlink(cr, uid, ids, context)
    
    @api.model
    def create(self,vals):
        
        new_id = super(acesmanpowerjob, self).create(vals)
        
        job_obj = self.env['acesmanpowerjob'].search([('id', '=', new_id.id)])
        event_id = job_obj.acesmanpowerevent_id.id
        event_job_user_id = job_obj.acesmanpowerevent_id.user_id.id
        
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
                    manager = self.env['acesmanpoweruser'].search([('user_id','=',manager_id)])
                    
            # Send SMS to the manager    
            initiator_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
            link = "http://192.168.2.124:8060/managejob.php?jid=" + str(new_id.id)
            to = manager.mobile or 0
            mess = 'A new Job position has been proposed by ' + initiator_obj.name + '.  Follow URL link to take action, ' + link
            
            thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
            ames={}
            ames['msg'] = mess
            ames['gateway_id'] = 1
            ames['mobile'] = to
            ames['name'] = thelink + "to=" + to + "&" + 'text=' + mess
            self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
            
            # Send Notification
            sysm = {}
            sysm['model'] = 'acesmanpowerjob'
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
                subject += "Open Position"
                url = (str('http://192.168.2.124:8060/web')+
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
        stage_id = values.get('stage_id',False)
        
        job_obj = self.env['acesmanpowerjob'].search([('id', '=', self.id)])
        
        if stage_id == 'reject':
            self.send_notification_mail()
        
        if stage_id == 'approve':
            
            mail_server = None
            mail_server_obj = self.pool.get('ir.mail_server')
            mail_server_ids = mail_server_obj.search(self._cr, SUPERUSER_ID, [], order='sequence', limit=1)
            if mail_server_ids:
                mail_server = mail_server_obj.browse(self._cr, SUPERUSER_ID, mail_server_ids[0])
            
            job_obj = self.env['acesmanpowerjob'].search([('id', '=', self.id)])
            mobile = self.env['acesmanpowerjob'].search([('id','=',self.id)]).acesmanpoweruser_id.mobile
            
            thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
            link = "http://192.168.2.124:8060/?id=" + str(self.id) + '%26jid=' + str(job_obj.id)
            mess = 'Open position,' + self.name + ' , has been approved. Follow URL link to take action, ' + link
            ames={}
            ames['msg'] = mess
            ames['gateway_id'] = 2
            ames['mobile'] = mobile
            ames['name'] = thelink + "to=" + mobile + "&" + 'text=' + mess
            self.pool.get('sms.smsclient.queue').create(self._cr,SUPERUSER_ID,ames)
            
            manager_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
            
            if mail_server:
                body = subject = ''
                subject += "Open Position"
                url = (str('http://192.168.2.124:8060/web')+
                             "?db=%s#id=%d&view_type=form&model=acesmanpowerjob"%(self._cr.dbname,job_obj.id))
                body += 'A new Open Position,'+ self.name +' has been approved by ' + manager_obj.name + '.  Follow URL link to take action, ' + url
                    
                manager_obj = self.env['res.users'].search([('id','=',self._uid)])
                manager_mail =  manager_obj.login
                
                acesmanpoweruser_id = self.env['acesmanpowerjob'].search([('id','=',self.id)]).acesmanpoweruser_id.id
                rceiver_obj = self.env['res.users'].search([('acesmanpoweruser_id','=',acesmanpoweruser_id)])
                rceiver_email =  rceiver_obj.login
                
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
            sysm['model'] = 'acesmanpowerjob'
            sysm['type'] = 'notification'
            sysm['subject'] = 'SMS'
            sysm['res_id'] = self.id
            sysm['body'] = 'Invitations has been sent to job initiator'  
            self.pool.get('mail.message').create(self._cr,SUPERUSER_ID,sysm)
        
        return super(acesmanpowerjob, self).write(values)
    
    def send_notification_mail(self):
        
        # Send SMS to the manager    
        manager_obj = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)]) # Manager
        mobile = self.env['acesmanpowerjob'].search([('id','=',self.id)]).acesmanpoweruser_id.mobile

        to = mobile or 0
        mess = 'Your request for the Open position has been denied by ' + manager_obj.name
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
            subject += "Open Position"
            body += 'Your request for the Open Position has been denied by ' + manager_obj.name
             
            manager_obj = self.env['res.users'].search([('id','=',self._uid)])
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
        jobposition_ids = property_ids = []
        log_in_user = property_user_id = False
        # Find the log in user and his related property user id
        
        if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
            log_in_user = uid
            property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
            print "Log In user {'%s'} = Property User {'%s'}"%(log_in_user,property_user_id[0])
        else:
            pass
        
        # Find property and related property ids of log in user with related to property user
        if log_in_user and property_user_id:
            # Direct Property
            property_id = manpower_user_obj.browse(cr,uid,property_user_id[0],context).property_id.id
            # Other Properties
            for obje in manpower_user_obj.browse(cr,uid,property_user_id,context):
                property_ids = [obj.id for obj in obje.property_ids]
            property_ids.append(property_id)
            
            print "property_id=",property_id,property_ids
                
        # Find all the job positions which is linked with any of the property
        if property_ids:
            jobposition_ids = jobposition_obj.search(cr,uid,[('acesmanpowerproperty_id','in',list(set(property_ids)))],context=context)
            print "jobposition_ids=",jobposition_ids
                
        domain = [('id','in',jobposition_ids)]
        
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if flag_grop_user or flag_group_admin or flag_group_consultant:     
            domain = []
        
        print "Domain=",domain
        
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