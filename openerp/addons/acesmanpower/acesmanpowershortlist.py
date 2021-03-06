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
import urllib, cStringIO

from openerp import api, tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.modules.module import get_module_resource

class acesmanpowershortlist(osv.osv):
    _name = 'acesmanpowershortlist'
    _description = "For Assessment"
    _order = "name asc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _default_user(self, cr, uid, context=None):
        return context.get('active_id')
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        if value:
            return self.write(cr, uid, [ids], {'image': tools.image_resize_image_big(value)}, context=context)
        return True

    def _set_image_url2(self, cr, uid, ids, name, value, args, context=None):
        file = cStringIO.StringIO(urllib.urlopen(URL).read())
        return self.write(cr, uid, [ids], {'image': tools.image_resize_image_big(file)}, context=context)

    @api.multi
    def set_assessment_stage(self):
        values = {}
        values['stage_id'] = self._context.get('stage_id')
        shortlist_obj = self.env['acesmanpowershortlist'].search([('id','=',self.id)])
        if not shortlist_obj.acesmanpowerjob_id:
            raise osv.except_osv(_('Warning!'), _("Please fill up Job Applied details before moving to final assessment stage"))
        return super(acesmanpowershortlist, self).write(values)
    
    @api.multi
    def back_to_screening(self):
        action = self.env.ref('acesmanpower.ir_actions_server_acesmanpowerscreening')
        result = action.read()[0]
        return result
    
    @api.multi
    def set_assessment_result(self):
        values = {}
        values['assess_id'] = self._context.get('assess_id')
        if self._context.get('assess_id') == 'red':
            values['stage_id'] = 2
        else: 
            values['stage_id'] = 3
        return super(acesmanpowershortlist, self).write(values)
    
    @api.multi
    def move_to_data_pool(self):
        values = {}
        stage_id = self._context.get('stage_id')
        if stage_id == 6:
            shortlist_obj = self.env['acesmanpowershortlist'].search([('id','=',self.id)])
            if not shortlist_obj.interview_sheet:
                raise osv.except_osv(_('Warning!'), _("Please upload Interview Sheet before you proceed to Approved Data Pool"))
        values['stage_id'] = stage_id
        return super(acesmanpowershortlist, self).write(values)
        
    def remove_from_data_pool(self,cr,uid,ids,context=None):
        if context is None:
            context = {}
        self.unlink(cr, uid, ids, context=context)
        
    def import_file(self, cr, uid, ids, context=None):
        return
        
    @api.model
    def create(self, vals):
#         jobseeker_id = self._context['acesjobseeker_id']
#         screen_objs = self.env['acesmanpowerscreening'].search([('acesjobseeker_id','=',jobseeker_id)])
#         screen_ids = [obj.id for obj in screen_objs]
#         values = {}
#         for screen_obj in self.env['acesmanpowerscreening'].browse(screen_ids):
#             values['state_id'] = 'shortlisted'
#             values['from_short_list'] = True
#             screen_obj.write(values)
#         jobseeker_obj = self.env['acesjobseeker'].search([('id','=',jobseeker_id)])
#         jobseeker_obj.write({'stage_id':'shortlisted'})
        return osv.osv.create(self, vals)
    
    @api.multi
    def write(self, values):
        stage_id = values.get('stage_id',False)
        if stage_id == 6:
            if not (values.get('interview_sheet',False) or self.interview_sheet):
                raise osv.except_osv(_('Warning!'), _("Please upload Interview Sheet before you proceed to Approved Data Pool"))
            else:
                pass
        
        if not values.get('agency_consultant_ids',''):
            # TO DO - check if already any consultant id linked with this
            agency_consultant_ids = [ user_id.id for user_id in self.env['hr.employee'].search([('consultant','=',True)])]
            values['agency_consultant_ids'] = [(6, 0, agency_consultant_ids)]
            
        return super(acesmanpowershortlist, self).write(values)
    
    _columns = {
        
        'acesjobseeker_id': fields.many2one('acesjobseeker', 'Jobseeker', required=True),
        'name': fields.related('acesjobseeker_id', 'name', type='char', size=256, string='Name', store=True),
        'url_image': fields.related('acesjobseeker_id', 'url_image', type='char', size=500, string='Name', store=True ),
        
        'stage_id': fields.selection([(1, 'Pending Assessment'),(9, 'Request Result'),(2, 'Failed Assessment'),(3, 'Passed Assessment'),(4, 'For Interview'),(5, 'Selected'),(6, 'Approved Data Pool'),(7, 'Failed Interview'),(8, 'Unavailable'),(10, 'My Candidates')], 'Status', track_visibility='onchange'),
        
        #'assess_id': fields.selection([('green', 'Excellent'),('white', 'Very Good'),('yellow', 'Good'),('red', 'Fail')], 'Assessment Score', track_visibility='onchange' ),
        'assess_id': fields.selection([('green', 'Green'),('white', 'Clear'),('yellow', 'Yellow'),('red', 'Red')], 'Assessment Score', track_visibility='onchange' ),
        
        'assessment_date': fields.datetime('Create Date', readonly=True),
        
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated On', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
        'company_id': fields.many2one('res.company', 'Company'),
        'description': fields.text(string='Notes', ),
        
        'acesmanpowerjob_id': fields.many2one('acesmanpowerjob', 'Job Applied'),
        'acesmanpoweruser_id': fields.related('acesmanpowerjob_id', 'acesmanpoweruser_id', type="many2one", relation="acesmanpoweruser", string="Event Initiator", store=True),
        'acesmanpowerproperty_id': fields.related('acesmanpowerjob_id', 'acesmanpowerproperty_id', type="many2one", relation="acesmanpowerproperty", string="Property", store=True),
        'acesmanpowerevent_id': fields.related('acesmanpowerjob_id', 'acesmanpowerevent_id', type="many2one", relation="acesmanpowerevent", string="Trip Event", store=True),
        'agency_consultant_ids':fields.many2many('hr.employee','shortlist_consultant_rel','shortlist_id','consultant_id'),
        
        'interview_sheet_name':fields.char('Filename'),
        'interview_sheet': fields.binary('Interview Sheet'),
        
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Photo",
            help="This field holds the image used as photo for the applicant, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized photo", type="binary", multi="_get_image",
            store = {
                'acesmanpowershortlist': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized photo of the employee. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized photo", type="binary", multi="_get_image",
            store = {
                'acesmanpowershortlist': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized photo of the employee. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        
    }
    
    def _get_default_image(self, cr, uid, context=None):
        url_image = context.get('url_image')
        
        if url_image not in ('',False,None):
            raw_data = base64.b64encode(cStringIO.StringIO(urllib.urlopen(url_image).read()).getvalue())
        else:
            image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
            raw_data = open(image_path, 'rb').read().encode('base64')
        return tools.image_resize_image_big(raw_data)
    
    def candidates_on_process(self, cr, uid, ids, stage = None, context=None):
        if context is None:
            context = {}
            
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        shortlist_obj = self.pool.get('acesmanpowershortlist')
        property_obj = self.pool.get('acesmanpowerproperty')
        shortlist_ids = property_ids = []
        log_in_user = property_user_id = property_id = False
        
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
                
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_grop_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if (flag_grop_user or flag_group_admin) and property_id:
            all_child_ids = property_obj.search(cr,uid,[('id','child_of',[property_id])],context=context)
            if all_child_ids:
                property_ids.extend(all_child_ids)
                property_ids = list(set(property_ids))
                
        # Find all the short listed candidates who is linked with any of the property
        if property_ids:
            shortlist_ids = shortlist_obj.search(cr,uid,[('acesmanpowerproperty_id','in',list(set(property_ids)))],context=context)
            
        domain = [('stage_id', 'in', [1,3,4,5,9]),('id','in',shortlist_ids)]   
            
        if flag_grop_consultant:
            domain = domain[:-1]
            
        # This is a special condition to show data in the dash board of each and every user.
        if stage == None:
            stage = 25
            name_dict = {25:'All'}
            if shortlist_ids:
                domain = [('stage_id', 'in', [1,3,4,5,9]),('id','in',shortlist_ids)]
                if flag_grop_consultant:
                    domain = []
            
        print "Domain=1>",domain,stage
        value = {
                'name': _(name_dict[stage]),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesmanpowershortlist',
                'view_id': False,
                'domain': domain
                }
        return value
        
    
    def fetch_data(self, cr, uid, ids, stage=None, context=None):
        if context is None:
            context = {}
        print "-"*25
        
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        shortlist_obj = self.pool.get('acesmanpowershortlist')
        property_obj = self.pool.get('acesmanpowerproperty')
        shortlist_ids = property_ids = []
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
                
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_grop_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if (flag_grop_user or flag_group_admin) and property_id:
            all_child_ids = property_obj.search(cr,uid,[('id','child_of',[property_id])],context=context)
            if all_child_ids:
                property_ids.extend(all_child_ids)
                property_ids = list(set(property_ids))
                
        # Find all the short listed candidates who is linked with any of the property
        if property_ids:
            shortlist_ids = shortlist_obj.search(cr,uid,[('acesmanpowerproperty_id','in',list(set(property_ids)))],context=context)
                
        # Name and Domain selection for final data filtering
        if isinstance(stage, int):
            domain = [('stage_id', '=', stage),('id','in',shortlist_ids)]
            name_dict = {1:'Pending Assessment Result',9:'Waiting Results',4:'For Interview',
                         6:'Approved Data Pool',10:'My candidates'}
        elif isinstance(stage, tuple):
            domain = [('stage_id', 'in', stage),('id','in',shortlist_ids)]
            name_dict = {stage:'Qualified'}
        else:
            domain = [('id','in',shortlist_ids)]
                
        if flag_grop_consultant:
            domain = domain[:-1]
            
        # This is a special condition to show data in the dash board of each and every user.
        if stage == None:
            stage = 25
            name_dict = {25:'All'}
            if shortlist_ids:
                domain = [('id','in',shortlist_ids),('stage_id', 'in', [1,3,4,5,9])]
                if flag_grop_consultant:
                    domain = []
            
        print "Shortlist Domain =>",domain,stage
        value = {
                'name': _(name_dict[stage]),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesmanpowershortlist',
                'view_id': False,
                'domain': domain
                }
        print "-"*25
        return value
    
    _defaults = {
        'stage_id': 1,
        'image': _get_default_image,
        'acesjobseeker_id': lambda self, cr, uid, c: c.get('acesjobseeker_id', False),
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'acesmanpowershortlist', context=c),
    }
    