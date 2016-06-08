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
from openerp.osv import osv
from openerp.tools.translate import _

class mail_message(osv.osv):
    _inherit = 'mail.message'
    
    def fetch_data(self, cr, uid, ids,context=None):
        '''
        This method will fetch data for the regular menu click of the user
        '''
        if context is None:
            context = {}
            
            
        user_id = self.pool.get('res.users').search(cr,uid,[('id','=',uid)])
        
        print "#"*25
        #print "UID",user_id 
        partner_id = self.pool.get('res.users').browse(cr,uid,uid,context).partner_id.id
        #print "partner ID----->",partner_id
        
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        property_obj = self.pool.get('acesmanpowerproperty')
        property_ids = partner_ids =  []
        
        
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
            #print "property_id=",property_ids
            
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant')
        
        if (flag_grop_user or flag_group_admin) and property_id:
            all_child_ids = property_obj.search(cr,uid,[('id','child_of',[property_id])],context=context)
            if all_child_ids:
                property_ids.extend(all_child_ids)
                property_ids = list(set(property_ids))
                
        #print "property_ids",property_ids
        
        if len(property_ids):
        
            if len(property_ids) > 1:
                cr.execute("SELECT user_id FROM acesmanpoweruser WHERE property_id in %s"%(tuple(property_ids),))
            else:
                cr.execute("SELECT user_id FROM acesmanpoweruser WHERE property_id in (%s)"%(tuple(property_ids)))
                
            rst = cr.fetchall()
            user_ids = [record[0] for record in rst if record[0] != None]
            #print "ALLLL USES",user_ids
            
            if len(user_ids) > 1:
                cr.execute("SELECT partner_id FROM res_users WHERE id in %s"%(tuple(user_ids),))
            else:
                cr.execute("SELECT partner_id FROM res_users WHERE id in (%s)"%(tuple(user_ids)))
            rst = cr.fetchall()
            partners = [record[0] for record in rst if record[0] != None]
            #print "ALL PARTNERS",partner_ids
            
            if partner_ids:
                partner_ids.extend(partners)
            else:
                partner_ids.append(partner_id)
            
            if len(partner_ids) > 1:
                cr.execute("SELECT mm.id,mm.subject , mm.body , mm.type"
                        " FROM mail_message mm" 
                        " WHERE mm.author_id IN %s AND mm.model = 'acesmanpowerevent'"%(tuple(partner_ids),))
            else:
                cr.execute("SELECT mm.id,mm.subject , mm.body , mm.type"
                        " FROM mail_message mm" 
                        " WHERE mm.author_id IN (%s) AND mm.model = 'acesmanpowerevent'"%(tuple(partner_ids)))
            
            rst = cr.fetchall()
            message_ids = [record[0] for record in rst if record[0] != None]
            domain = [('id','in',message_ids)]
        else:
            domain = [('id','=',0)]
        
        if flag_group_consultant:     
            domain = []
            
        try:
            dummy, view_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'acesmanpower', 'view_message_form_inherit')
        except ValueError, e:
            view_id = False
            
        print "Message Domain -->",domain
        value = {
                'name': _('Messages'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'mail.message',
                'view_id': False,
                'domain': domain
                }
        print "-"*25
        return value