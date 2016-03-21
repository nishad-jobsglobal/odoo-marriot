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
import os
import re
import base64
import subprocess

import logging
from openerp import api
from openerp import tools
from openerp.osv import osv, fields

_logger = logging.getLogger(__name__)


class cv_dropbox(osv.osv):
    
    _name = 'cv.dropbox'
    _description = "CV Dropbox"
    _order = "id desc" 
    
    _columns = {
                'name' : fields.char("Description"),
                'cv_filename':fields.char('Filename'),
                'drop_cv': fields.binary('Drop CV'),
                'drop_cv_file_name' : fields.char(string='Image Filename'),
                'text': fields.text()
                }
    
    @api.model
    def create(self,vals,uid=None):
        
        res_id = super(cv_dropbox, self).create(vals)
        
        directory_path =  self.env['ir.config_parameter'].get_param('ir_attachment.cv_dropbox')
        login_user_id = self.env['res.users'].browse([uid]) if uid else self.env.user.id
        
        for obj in self.browse([res_id.id]):
            file_name = obj.drop_cv_file_name             # Uploaded file name 
            binary_data = obj.drop_cv                     # Uploaded file content
            datas = base64.b64decode(binary_data)         # Decoded data

        directory_path = directory_path.split(':')[1]
        path = re.sub('[.]', '', directory_path)
        path = path.strip('/\\')
        
        goal_dir = os.path.join(os.getcwd(), path)
        if not os.path.isdir(goal_dir):
            os.makedirs(goal_dir)
            subprocess.call(['chmod', '-R', 'ugo+rwx', goal_dir])
        
        filename = goal_dir + '/%s_%s' % (login_user_id,file_name)
        try:
            with open(filename, 'w') as fp:
                fp.write(datas)
                fp.close()
            subprocess.call(['chmod', '-R', 'ugo+rwx', filename])
        except IOError:
            _logger.exception("_file_write writing %s", filename)
                            
        return res_id
    
class cv_byemail(osv.osv):
    _name = 'cv.byemail'
    _description = "CV Received by email"
    _order = "id desc" 
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    _columns = {
                'name' : fields.char("Subject / Applicants Name"),
                'partner_name': fields.char("Applicant's Name"),
                'email_from': fields.char('Email', size=128, help="These people will receive email."),
                'email_cc': fields.text('Watchers Emails', size=252, help="These email addresses will be added to the CC field of all inbound and outbound emails for this record before being sent. Separate multiple email addresses with a comma"),
                'partner_id': fields.many2one('res.partner', 'Contact'),
                'partner_phone': fields.char('Phone', size=32),
                'partner_mobile': fields.char('Mobile', size=32),
                'user_id': fields.many2one('res.users', 'Responsible', track_visibility='onchange'),
                'reference': fields.char('Referred By'),
                'message_last_post':fields.datetime("Date"),
                }
    
    _defaults = {
        'user_id': lambda s, cr, uid, c: uid
    }
    
    def message_new(self, cr, uid, msg, custom_values=None, context=None):
        """ Overrides mail_thread message_new that is called by the mailgateway
            through message_process.
            This override updates the document according to the email.
        """
        if custom_values is None:
            custom_values = {}
        val = msg.get('from').split('<')[0]
        defaults = {
            'name':  msg.get('subject') or _("Marriot"),
            'partner_name': val,
            'email_from': msg.get('from'),
            'email_cc': msg.get('cc'),
            'user_id': False,
            'partner_id': msg.get('author_id', False),
        }
        if msg.get('priority'):
            defaults['priority'] = msg.get('priority')
        defaults.update(custom_values)
        return super(cv_byemail, self).message_new(cr, uid, msg, custom_values=defaults, context=context)
    
class job_position(osv.osv):
    _name = 'job.position'
    _description = "job Position"
    _order = "id desc" 
    _columns ={
               'name' : fields.char("Name")
               }
    
class job_industry(osv.osv):
    _name = 'job.industry'
    _description = "Job Industry"
    _order = "id desc" 
    _columns ={
               'name' : fields.char("Name")
               }
    
class job_posting(osv.osv):
    _name = 'job.posting'
    _description = "Job Posting"
    _order = "id desc" 
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        if value:
            return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
        return True
    
    _columns = {
                'posting_intro': fields.char("Posting Introduction"),
                'posting_title':fields.char("Post Title"),
                'name' : fields.char("Name"),
                'url_image': fields.char(size=500, string='Choose Page URL'),
                'recruit_date':fields.date("Recruit Date"),
                'job_locations':fields.many2many('res.country','res_country_rel','job_location_id','country_id',"Job Locations"),
                'recruit_locations':fields.many2many('res.country','res_recruitment_country_rel','recruit_location_id','country_id',"Recruitment Location"),
                'jobs':fields.many2many('job.position','job_position_rel','job_id','job_position_id',"Jobs"),
                'job_industry':fields.many2many('job.industry','job_industry_rel','job_id','industry_id',"Industry"),
                'job_details':fields.text("Details"),
                'publish':fields.boolean("Unpublished Avert"),
                'image': fields.binary("Logo",
                        help="This field holds the image used as photo for the applicant, limited to 1024x1024px."),
                'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                    string="Medium-sized photo", type="binary", multi="_get_image",
                    store = {
                        'job.posting': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                    },
                    help="Medium-sized photo of the job description. It is automatically "\
                         "resized as a 128x128px image, with aspect ratio preserved. "\
                         "Use this field in form views or some kanban views."),
                
                
                }