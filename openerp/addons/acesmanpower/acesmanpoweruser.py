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
from psycopg2 import IntegrityError

from openerp import tools
from openerp import api
from openerp.osv import osv, fields
from openerp import SUPERUSER_ID
from openerp.tools.translate import _
from openerp.modules.module import get_module_resource

class acesmanpoweruser(osv.osv):
    _name = 'acesmanpoweruser'
    _description = "Recruitment Users"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        if value:
            return self.write(cr, uid, [ids], {'image': tools.image_resize_image_big(value)}, context=context)
        return True
    
    _columns = {
        'name': fields.char(size=256, string='Name', required=True, ),
        'username': fields.char(size=256, string='Username',  ),
        'password': fields.char(size=256, string='Password', required=True, ),
        
        'access_id': fields.selection([('staff', 'Property User'),('manager','Property Manager'),('user','Group User'),('admin','Group Manager')], 'Role / Access Level'),
        'email': fields.char(size=100, string='Email', required=True ),
        'mobile': fields.char(size=100, string='Mobile', required=True),
	'position': fields.char(size=100, string='Position'),
        'job_title': fields.char(size=100, string='Job Title'),
	'street': fields.char(size=256, string='Street', ),
        'city': fields.char(size=256, string='City', ),
        'country_id': fields.many2one('res.country', 'Country'),
        
        'company_id': fields.many2one('res.company', 'Parent Company', required=True),
        'user_id': fields.many2one('res.users', 'Related User'),
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated On', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
        'description': fields.text(string='Notes', ),
        'consultant':fields.boolean('Consultant'),
        
        'property_id': fields.many2one('acesmanpowerproperty', 'Property', required=True),
        'property_ids': fields.many2many('acesmanpowerproperty','acesmproperty_acesmuser_rel', 'acesmanpoweruser_id', 'acesmanpowerproperty_id', string="Other Properties"),
        
        'acesmanpowerevent_ids': fields.one2many('acesmanpowerevent','acesmanpoweruser_id','Recruitment Event'),
        
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Photo",
            help="This field holds the image used as photo for the applicant, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized photo", type="binary", multi="_get_image",
            store = {
                'acesmanpoweruser': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized photo of the employee. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized photo", type="binary", multi="_get_image",
            store = {
                'acesmanpoweruser': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized photo of the employee. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
    }
    
    _sql_constraints = [
        ('email_key', 'UNIQUE (email)',  'You can not have two users with the same username !')
    ]
    
    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))
        
    _defaults = {
        'image': _get_default_image,
        'access_id': 'staff',
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
    }
    
    def onchange_email(self, cr, uid, ids, email, username, context = None):
        values = {'username': '' }
        if email or '':
            email = email.strip(' \t\n\r')
        if username == '':
            values['username'] = email
        return {'value': values}
    
    @api.model
    def create(self,vals):
        
        login_user = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
        if not vals['access_id']:
            raise osv.except_osv(_('Warning!'), _("You should set a Role/Access Level for the new user"))
        if login_user.access_id == 'staff' and vals['access_id'] != 'staff':
            raise osv.except_osv(_('Warning!'), _("You can't create a user with a higher Role/Access Level than you !"))
        if login_user.access_id == 'manager' and vals['access_id'] in ('user','admin'):
            raise osv.except_osv(_('Warning!'), _("You can't create a user with a higher Role/Access Level than you !"))
        if login_user.access_id == 'user' and vals['access_id'] == 'admin':
            raise osv.except_osv(_('Warning!'), _("You can't create a user with a higher Role/Access Level than you !"))
        
        aces_object = super(acesmanpoweruser, self).create(vals)
        
        auser = {}
        auser['name'] = aces_object.name
        auser['email'] = aces_object.email
        auser['acesmanpoweruser_id'] = aces_object.id
        auser['login'] = aces_object.email
        auser['password'] = aces_object.password
        auser['new_password'] = aces_object.password
        auser['mobile'] = aces_object.mobile
        auser['company_id'] = aces_object.company_id.id
        company_ids = []
        company_ids.append(aces_object.company_id.id)
        auser['company_ids'] = company_ids
        
        print "auser",auser
        
        external_id_model = self.env['ir.model.data']
        group_portal_ref = external_id_model.get_object_reference('base', 'recruitment_portal')
        group_portal_id = group_portal_ref and group_portal_ref[1] or False
        
        print "Portal =",group_portal_id
        
        group_portal_ref1 = external_id_model.get_object_reference('base', 'recruitment_portal_special')
        group_portal_id1 = group_portal_ref1 and group_portal_ref1[1] or False
        
        print "Special Portal =",group_portal_id1
        
        employee_ref = external_id_model.get_object_reference('base', 'group_user')
        employee_red_id = employee_ref and employee_ref[1] or False
        
        sms_ref = external_id_model.get_object_reference('smsclient', 'group_sms_user')
        sms_ref_id = sms_ref and sms_ref[1] or False
        
        print "employee_red_id",employee_red_id
        
        staff_id = manager_id = gp_user_id = gp_admin_id = False
            
        if vals['access_id'] == 'staff':
            staff = external_id_model.get_object_reference('base', 'group_marriot_property_user')
            staff_id = staff and staff[1] or False
            auser['groups_id'] = [(6, 0, [employee_red_id,group_portal_id,group_portal_id1,staff_id,sms_ref_id])]
            
        if vals['access_id'] == 'manager':
            manager = external_id_model.get_object_reference('base', 'group_marriot_property_admin')
            manager_id = manager and manager[1] or False
            auser['groups_id'] = [(6, 0, [employee_red_id,group_portal_id,group_portal_id1,manager_id,sms_ref_id])]
            
        if vals['access_id'] == 'user':
            gp_user = external_id_model.get_object_reference('base', 'group_marriot_group_property_user')
            gp_user_id = gp_user and gp_user[1] or False
            auser['groups_id'] = [(6, 0, [employee_red_id,group_portal_id,group_portal_id1,gp_user_id,sms_ref_id])]
            
        if vals['access_id'] == 'admin':
            gp_admin = external_id_model.get_object_reference('base', 'group_marriot_group_property_admin')
            gp_admin_id = gp_admin and gp_admin[1] or False
            auser['groups_id'] = [(6, 0, [employee_red_id,group_portal_id,group_portal_id1,gp_admin_id,sms_ref_id])]
            
        print "auser['groups_id']",auser['groups_id']
        
        
        user_id = self.pool.get('res.users').create(self._cr,SUPERUSER_ID,auser)
        value = {}
        value['user_id'] = user_id
        aces_object.write(value)
        return aces_object
        
    @api.multi
    def write(self, values):
        
        access_id = values.get('access_id',False)
        login_user = self.env['acesmanpoweruser'].search([('user_id','=',self._uid)])
        obj = self.env['acesmanpoweruser'].search([('id','=',self.id)])
        
        #if not access_id and obj.access_id != False:
        #    raise osv.except_osv(_('Warning!'), _("You should set a Role/Access Level for the new user"))
        if login_user.access_id == 'staff' and access_id != 'staff':
            raise osv.except_osv(_('Warning!'), _("You can't create a user with a higher Role/Access Level than you !"))
        if login_user.access_id == 'manager' and access_id in ('user','admin'):
            raise osv.except_osv(_('Warning!'), _("You can't create a user with a higher Role/Access Level than you !"))
        if login_user.access_id == 'user' and access_id == 'admin':
            raise osv.except_osv(_('Warning!'), _("You can't create a user with a higher Role/Access Level than you !"))
        
        return super(acesmanpoweruser, self).write(values)
    
    def fetch_data(self, cr, uid, ids,context=None):
        if context is None:
            context = {}
        print "-"*25
        
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        log_in_user = property_id = property_user_id = False
        
        # Find the log in user and his related property user id
        if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
            log_in_user = uid
            property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
        
        # Find property and related property ids of log in user with related to property user
        if log_in_user and property_user_id:
            # Direct Property
            property_id = manpower_user_obj.browse(cr,uid,property_user_id[0],context).property_id.id
            
        flag_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_property_user')
        flag_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_property_admin')
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        domain = [('user_id','=',uid)]
        if flag_user and log_in_user and property_user_id:
            domain = [('id','=',property_user_id)]
        if flag_admin and log_in_user and property_user_id:
            property_users = manpower_user_obj.search(cr,uid,[('property_id','=',property_id)])
            domain = [('id','in',property_users)]
        if (flag_grop_user or flag_group_admin) and property_id:
            property_users = manpower_user_obj.search(cr,uid,[('property_id','child_of',property_id)])
            domain = [('id','in',property_users)]
            
        if flag_group_consultant:
            domain = []
            
        print "User Domain=",domain
        value = {
                'name': _('Users'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesmanpoweruser',
                'view_id': False,
                'domain': domain
                }
        print "-"*25
        return value
    
class res_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    _columns = {
                'acesmanpoweruser_id': fields.many2one('acesmanpoweruser', 'Recruitment User'),
                }
    
    def _get_company_restricted_groups(self,cr,uid):
        comapny_id = self.pool['res.users']._get_company(cr,uid)
        cr.execute("SELECT gid FROM res_company_groups_rel WHERE cid="+str(comapny_id))
        company_groups = cr.fetchall()
        if not company_groups:
            cr.execute("SELECT parent_id FROM res_company WHERE id="+str(comapny_id))
            rst = cr.fetchone()
            parent_company_id = rst[0]
            cr.execute("SELECT gid FROM res_company_groups_rel WHERE cid="+str(parent_company_id))
            company_groups = cr.fetchall()
        company_groups_ids = [gp[0] for gp in company_groups]
        return company_groups_ids or []
    
    def _get_groups_of_users(self,cr,uid):
        cr.execute("SELECT gid FROM res_groups_users_rel WHERE uid="+str(uid))
        user_groups = cr.fetchall()
        user_groups_ids = [gp[0] for gp in user_groups]
        return user_groups_ids or []
    
    def _get_users_of_group(self,cr,uid,group_id):
        cr.execute("SELECT uid FROM res_groups_users_rel WHERE gid="+str(group_id))
        all_users = cr.fetchall()
        all_users = [user[0] for user in all_users]
        return all_users
    
    
    def validate_groups(self,cr,uid,context=None):
        vals = {}
        company_groups_ids = self._get_company_restricted_groups(cr,uid)
        user_groups_ids = self._get_groups_of_users(cr,uid)
        if company_groups_ids and user_groups_ids:
            common_group_ids = set(company_groups_ids).intersection(user_groups_ids)
            if common_group_ids:
                unlink_ids = list(set(user_groups_ids).difference(common_group_ids))
                vals = {'groups_id': [(6,0,unlink_ids)]}
            elif user_groups_ids:
                vals = {'groups_id': [(6,0,user_groups_ids)]}
        return vals
    
#     def create(self, cr, uid, values, context=None):
#         print "values",values
#         res = ''
#         try:
#             res = super(res_users, self).create(cr, uid, values, context)
#         except IntegrityError as e:
#             user_name = values['login']
#             print "user_name==",user_name
#             #raise exceptions.ValidationError("Entered Date Should be greter then Today")
#             osv.except_osv(_('Warning!'),_('User %s is already existing, Please choose another username !')%(user_name))
#         except ValueError:
#             user_name = values['login']
#             print "user_name==",user_name
#             osv.except_osv(_('Warning!'),_('User %s is already existing, Please choose another username !')%(user_name))
#              
#         return res or ''
    
    def write(self, cr, uid, ids, vals, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        admin_comapny_id = self.pool['res.users']._get_company(cr,SUPERUSER_ID) or None
        user_comapny_id = self.pool['res.users']._get_company(cr,ids[0]) or None
        if user_comapny_id == admin_comapny_id:
            # Check and update the head office processing teams status in the Employee master
            cr.execute("SELECT id FROM res_groups WHERE name='Member of Head office Processing Team'")
            group_id = cr.fetchone()[0]
            initial_users = self._get_users_of_group(cr,uid,group_id)
            # Update user with all the other updates.
            res = super(res_users, self).write(cr, uid, ids, vals, context)
            final_users = self._get_users_of_group(cr,uid,group_id)
            if len(list(set(initial_users)-set(final_users))) > 0:
                users = list(set(initial_users)-set(final_users))
                status = False
            elif len(list(set(final_users)-set(initial_users))) > 0:
                users = list(set(final_users)-set(initial_users))
                status = True
            else:
                users = list(set(initial_users)  & set(final_users))
                status = True
                
            for user_id in users:
                employee_id = self.pool['hr.employee'].search(cr,uid,[('user_id','=',user_id)])
                if not employee_id:
                    user_name = self.pool['res.users'].browse(cr,uid,[user_id]).name
                    raise osv.except_osv(_('Warning!'),_('User %s is not linked with an employee, Please link it first !')%(user_name))
                employee_obj = self.pool['hr.employee'].browse(cr,uid,[employee_id[0]])
                employee_obj.write({'consultant':status})
        else:
            res = super(res_users, self).write(cr, uid, ids, vals, context)
            # Check for all the possible groups with which this user is able to associate with
            for user_id in self.browse(cr, uid, ids, context=context):
                vals = self.validate_groups(cr,user_id.id,context=context)
            if vals:
                super(res_users, self).write(cr, uid, ids, vals, context)
        return res
    
class hr_employee(osv.osv):
    _name = "hr.employee"
    _inherit = "hr.employee"
    _columns = {
        'consultant':fields.boolean('Consultant'),
    }
