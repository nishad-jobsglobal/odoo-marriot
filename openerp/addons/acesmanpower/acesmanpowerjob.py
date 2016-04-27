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

from openerp.osv import osv, fields
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