#############################################################################
#
#    Jobs Global
#    Copyright (C) 2014-TODAY Jobs Global(http://www.jobsglobal.com).
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
#/#############################################################################

from openerp.osv import osv, fields
from openerp.tools.translate import _

class trip(osv.osv):
    _inherit = 'trip'
    _description = "Trip"
    
    _columns = {
                'property_id': fields.many2one('acesmanpowerproperty', 'Property'),
                'marriot_trip_id':fields.many2one('acesmanpowerevent', 'Recruitment Trip'),
                }
    
    def fetch_data(self, cr, uid, ids,context=None):
        if context is None:
            context = {}
        print "-"*25
        
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        property_obj = self.pool.get('acesmanpowerproperty')
        trip_obj = self.pool.get('trip')
        trip_ids = property_ids = []
        log_in_user = property_user_id = property_id = False
        # Find the log in user and his related property user id
        if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
            log_in_user = uid
            property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
            #print "Log In user {'%s'} = Property User {'%s'}"%(log_in_user,property_user_id[0])
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
            #print "Direct Property ID=",property_id,property_ids
        
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if (flag_grop_user or flag_group_admin) and property_id:
            all_child_ids = property_obj.search(cr,uid,[('id','child_of',[property_id])],context=context)
            if all_child_ids:
                property_ids.extend(all_child_ids)
                property_ids = list(set(property_ids))
                
        # Find all the short listed candidates who is linked with any of the property
        if property_ids:
            trip_ids = trip_obj.search(cr,uid,[('property_id','in',list(set(property_ids)))],context=context)
            print "trip_ids=",trip_ids
                
        domain = [('id','in',trip_ids)]
        
        if flag_group_consultant:     
            domain = [('property_id','!=',False)]
            
        print "Domain=",domain
        
        value = {
                'name': _("Trips"),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'trip',
                'view_id': False,
                'domain': domain
                }
        print "-"*25
        return value    