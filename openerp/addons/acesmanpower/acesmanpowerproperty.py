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

import openerp
from openerp import api
from openerp import tools
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp.modules.module import get_module_resource

class acesmanpowerproperty(osv.osv):
    
    _inherits = {
        'res.partner': 'partner_id',
                    }
     
    _name = 'acesmanpowerproperty'
    _description = "Property"
    _order = "id asc"
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
    
    @api.model
    def create(self, vals):
        agency_consultant_ids = [ user_id.id for user_id in self.env['hr.employee'].search([('consultant','=',True)])]
        vals['agency_consultant_ids'] = [(6, 0, agency_consultant_ids)]
        return super(acesmanpowerproperty, self).create(vals)
    
    @api.multi
    def write(self, vals):
        if not vals.get('agency_consultant_ids',''):
            # TO DO - check if already any consultant id linked with this
            agency_consultant_ids = [ user_id.id for user_id in self.env['hr.employee'].search([('consultant','=',True)])]
            vals['agency_consultant_ids'] = [(6, 0, agency_consultant_ids)]
        return super(acesmanpowerproperty, self).write(vals)

    _columns = {
        # Name & Email will inherit from res_partner
        #'name': fields.char(size=256, string='Name', required=True, ),
        #'email': fields.related('acesmanpoweruser_id', 'email', type='char', string='Email', readonly=True),
        
        'street': fields.char(size=256, string='Street', ),
        'city': fields.char(size=256, string='City', ),
        'country_id': fields.many2one('res.country', 'Country'),
        'acesmanpoweruser_id': fields.many2one('acesmanpoweruser', 'Responsible', track_visibility='onchange'),
        'mobile': fields.related('acesmanpoweruser_id', 'mobile', type='char', string='Mobile', readonly=True),
        
        'partner_id': fields.many2one('res.partner', required=True,
            string='Related Partner/Customer', ondelete='restrict',
            help='Partner-related data of the property', auto_join=True),
        'parent_id': fields.many2one('acesmanpowerproperty', 'Parent Property', select=True),
        'child_ids': fields.one2many('acesmanpowerproperty', 'parent_id', 'Child Properties'),
        
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
        'description': fields.text(string='Notes', ),
        
        'acesmanpowerevent_ids': fields.many2many('acesmanpowerevent', 'acesmproperty_acesmevent_rel', 'acesmanpowerproperty_id', 'acesmanpowerevent_id'),
        'agency_consultant_ids':fields.many2many('hr.employee','property_consultant_rel','property_id','consultant_id'), 
        
        'website': fields.char(size=160, string='Website', ),
        
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Photo",
            help="This field holds the image used as photo for the applicant, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized photo", type="binary", multi="_get_image",
            store = {
                'acesmanpowerproperty': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized photo of the employee. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized photo", type="binary", multi="_get_image",
            store = {
                'acesmanpowerproperty': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized photo of the employee. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        
    }
    
    name = openerp.fields.Char(related='partner_id.name', inherited=True)
    email = openerp.fields.Char(related='partner_id.email', inherited=True)
    
    
    @api.multi
    def action_sent_mail(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        template = self.env.ref('acesmanpower.email_template_edi_acesmanpowerproperty', False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='acesmanpowerproperty',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
    
    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))
    
    _defaults = {
        'image': _get_default_image,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'acesmanpowerproperty', context=c),
        'acesmanpoweruser_id': lambda self, cr, uid, c: c.get('acesmanpoweruser_id', False),
    }
    
    def fetch_data(self, cr, uid, ids,context=None):
        if context is None:
            context = {}
        print "-"*25
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        property_obj = self.pool.get('acesmanpowerproperty')
        all_property_ids = property_ids = []
        log_in_user = property_user_id = False
        # Find the log in user and his related property user id
        if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
            log_in_user = uid
            property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
            print "Log In user {'%s'} = Property User {'%s'}"%(log_in_user,property_user_id[0])
        
        # Find property and related property ids of log in user with related to property user
        if log_in_user and property_user_id:
            # Direct Property
            property_id = manpower_user_obj.browse(cr,uid,property_user_id[0],context).property_id.id
            # Other Properties
            for obje in manpower_user_obj.browse(cr,uid,property_user_id,context):
                property_ids = [obj.id for obj in obje.property_ids]
            property_ids.append(property_id)
            print "property_id=",property_id,property_ids
                
        # Find all the short listed candidates who is linked with any of the property
        if property_ids:
            all_property_ids = property_obj.search(cr,uid,[('id','in',list(set(property_ids)))],context=context)
            print "all_property_ids=",all_property_ids
        domain = [('id','in',all_property_ids)]
            
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if flag_grop_user or flag_group_admin or flag_group_consultant:     
            domain = []
        print "Domain=",domain
        value = {
                'name': _('Properties'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesmanpowerproperty',
                'view_id': False,
                'domain': domain
                }
        print "-"*25
        return value
