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
from openerp.modules.module import get_module_resource

class acesmanpowerproperty(osv.osv):
    _name = 'acesmanpowerproperty'
    _description = "Property"
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
            return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
        return True
    
    @api.model
    def create(self, vals):
        agency_consultant_ids = [ user_id.id for user_id in self.env['acesmanpoweruser'].search([])]
        vals['agency_consultant_ids'] = [(6, 0, agency_consultant_ids)] 
        res = super(acesmanpowerproperty, self).create(vals)
        return res 

    _columns = {
        'name': fields.char(size=256, string='Name', required=True, ),

        'email': fields.related('acesmanpoweruser_id', 'email', type='char', string='Email', readonly=True),
        'mobile': fields.related('acesmanpoweruser_id', 'mobile', type='char', string='Mobile', readonly=True),
        
        'street': fields.char(size=256, string='Street', ),
        'city': fields.char(size=256, string='City', ),
        'country_id': fields.many2one('res.country', 'Country'),
        'acesmanpoweruser_id': fields.many2one('acesmanpoweruser', 'Responsible', track_visibility='onchange'),
        
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
        'description': fields.text(string='Notes', ),
        
        'acesmanpowerevent_ids': fields.many2many('acesmanpowerevent', 'acesmproperty_acesmevent_rel', 'acesmanpowerproperty_id', 'acesmanpowerevent_id'),
        'agency_consultant_ids': fields.many2many('acesmanpoweruser','acesmproperty_acesuser_rel','acesmanpowerproperty_id','acesmanpoweruser_id'),
        
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
    
    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))
    
    _defaults = {
        'image': _get_default_image,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
        'acesmanpoweruser_id': lambda self, cr, uid, c: c.get('acesmanpoweruser_id', False),
    }
