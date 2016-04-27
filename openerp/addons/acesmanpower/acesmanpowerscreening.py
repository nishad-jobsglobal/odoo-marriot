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

from openerp.tools.translate import _
from openerp.osv import osv, fields

class acesmanpowerscreening(osv.osv):
    _name = 'acesmanpowerscreening'
    _description = "Recruitment Screening"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    _columns = {
        'acesjobseeker_id': fields.many2one('acesjobseeker', 'Jobseeker', required=True),
        'trip_id':fields.many2one('acesmanpowerevent',"Recruitment Trip"),
        'name': fields.related('acesjobseeker_id', 'name', string="Name", type="char", size=256, store=True, readonly=True),
        'state_id': fields.selection([('new', 'New'),('shortlisted', 'Shortlisted')], 'Screening Status'),
        'url_image': fields.related('acesjobseeker_id', 'url_image', string="Photo", type="char", size=500, store=True, readonly=True),
        'q1': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Overall Experience'),
        'q2': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Communication Skills'),
        'q3': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Appearance'),
        'q4': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Body Proportionality'),
        'q5': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Skin Complexion'),
        'q6': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Hospitality Knowledge'),
        'q7': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'F&B Knowledge'),
        'q8': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Hygiene'),
        'q9': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'English Language'),
        'q10': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Attitude'),
        'q11': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Passionate/Energetic'),
        'q12': fields.selection([('1', '1'),('2', '2'),('3','3'),('4','4'),('5','5'),('6','6'),('7','7'),('8','8'),('9','9'),('10','10')], 'Smile/Willingness to Help Others'),
        'user_id': fields.many2one('res.users', 'Screened by', track_visibility='onchange'),
        'description': fields.text(string='Notes', ),
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
        'workin': fields.char('Willing to work in', size=500),
    }
    
    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'name' : 'Screening',
        'acesjobseeker_id': lambda self, cr, uid, context: context.get('acesjobseeker_id', False),
        'url_image': lambda self, cr, uid, context: context.get('url_image', False),
    }
    
    
    def fetch_data(self, cr, uid, ids,context=None):
        if context is None:
            context = {}
        print "-"*25
        
        flag_grop_user = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_user')
        flag_group_admin = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        log_in_user = property_id = property_user_id = False
        property_ids = final_trips = domain = []
        
        # Find the log in user and his related property user id
        if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
            log_in_user = uid
            property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
        # Find property and related property ids of log in user with linked to property user
        if log_in_user and property_user_id:
            # Direct Property
            property_id = manpower_user_obj.browse(cr,uid,property_user_id[0],context).property_id.id
            # Other Properties
            for obje in manpower_user_obj.browse(cr,uid,property_user_id,context):
                property_ids = [obj.id for obj in obje.property_ids]
            property_ids.append(property_id)
            
        print "UID PUID:",log_in_user,property_id
        print "Other property_ids:",property_ids
        print "-"*25
            
        # Select different trips linked to a screening
        cr.execute("""SELECT DISTINCT(trip_id) FROM acesmanpowerscreening""")
        rst = cr.fetchall()
        if rst not in (None,[],[None]):
            trip_ids = [record[0] for record in rst if record[0] != None]
            print "trip_ids",trip_ids
            for trip_id in trip_ids:
                print "trip_id=",trip_id
                cr.execute("""SELECT acesmanpowerproperty_id FROM acesmproperty_acesmevent_rel WHERE acesmanpowerevent_id=%s"""%(trip_id))
                rst = cr.fetchall()
                trip_property_ids = [record[0] for record in rst if record[0] != None]
                print 'trip_property_ids',trip_property_ids
                for pid in trip_property_ids:
                    if pid in list(set(property_ids)):
                        final_trips.append(trip_id)
                    else:
                        pass
            final_trips = list(set(final_trips))
            print "final_trips",final_trips
            if flag_group_admin or flag_grop_user:
                final_trips = trip_ids
                print "Admin final_trips",final_trips
            
            if len(final_trips):
                if len(final_trips) > 1:
                    cr.execute("""SELECT id FROM acesmanpowerscreening WHERE trip_id in %s"""%(tuple(final_trips),))
                else:
                    cr.execute("""SELECT id FROM acesmanpowerscreening WHERE trip_id in (%s)"""%(tuple(final_trips)))
                rst = cr.fetchall()
                screening_ids = [record[0] for record in rst if record[0] != None]
                print "screening_ids",screening_ids
                domain = [('id','in',screening_ids),('state_id','=','new')]
            else:
                domain = [('id','=',0)]
        
        # Jobs global consultants needs to see all data's to map the trip ID with each job seeker data.
        flag_group_consultant = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_consultant') 
        if flag_group_consultant:
            domain = [('state_id','=','new')]
        
        value = {
                'name': _('Jobseeker Screening'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesmanpowerscreening',
                'view_id': False,
                'domain': domain
                }
        print "-"*25
        return value
    
