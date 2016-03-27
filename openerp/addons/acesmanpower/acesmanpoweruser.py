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
from openerp import tools
from openerp.osv import osv, fields
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
            return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
        return True
    
    _columns = {
        'name': fields.char(size=256, string='Name', required=True, ),
        'username': fields.char(size=256, string='Username',  ),
        'password': fields.char(size=256, string='Password', required=True, ),
        
        'access_id': fields.selection([('staff', 'Recruitment Staff'),('manager','Manager'),('admin','Administrator')], 'Role / Access Level'),
        'email': fields.char(size=100, string='Email', required=True ),
        'mobile': fields.char(size=100, string='Mobile', required=True),
        
        'company_id': fields.many2one('res.company', 'Parent Company', required=True),
        'user_id': fields.many2one('res.users', 'Related User'),
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
        'description': fields.text(string='Notes', ),
        'consultant':fields.boolean('Consultant'),
        
        'property_id': fields.many2one('acesmanpowerproperty', 'Property', required=True),
        #'property_ids': fields.one2many('acesmanpowerproperty','acesmanpoweruser_id','Other Properties'),
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
        else:
            pass
        
        # Find property and related property ids of log in user with related to property user
        if log_in_user and property_user_id:
            # Direct Property
            property_id = manpower_user_obj.browse(cr,uid,property_user_id,context).property_id.id
            
        flag_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_property_user')
        flag_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_property_admin')
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        
        domain = [('user_id','=',uid)]
        if flag_user and log_in_user and property_user_id:
            domain = [('id','=',property_user_id)]
        if flag_admin and log_in_user and property_user_id:
            proerty_users = manpower_user_obj.search(cr,uid,[('property_id','=',property_id)])
            domain = [('id','in',proerty_users)]
        if flag_group_admin:
            domain = []
            
        print "Domain=",domain
        
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
    
    @api.multi
    def write(self, vals):
        print "="*25
        print "Users =",vals
        
        self.env.cr.execute("SELECT id FROM res_groups WHERE name='Member of Head office Processing Team'")
        group_id = self.env.cr.fetchone()[0]
        self.env.cr.execute("SELECT uid FROM res_groups_users_rel WHERE gid="+str(group_id))
        initial_users = self.env.cr.fetchall()
        initial_users = [user[0] for user in initial_users]
        
        # Update user with all the other updates.
        res = super(res_users, self).write(vals)
        
        self.env.cr.execute("SELECT uid FROM res_groups_users_rel WHERE gid="+str(group_id))
        final_users = self.env.cr.fetchall()
        final_users = [user[0] for user in final_users]
        
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
            employee_id = self.env['hr.employee'].search([('user_id','=',user_id)])
            employee_obj = self.env['hr.employee'].browse([employee_id.id])
            employee_obj.write({'consultant':status})
        return res
    
    
    
class hr_employee(osv.osv):
    _name = "hr.employee"
    _inherit = "hr.employee"
    _columns = {
        'consultant':fields.boolean('Consultant'),
    }
    