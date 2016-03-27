# -*- coding: utf-8 -*-
#/#############################################################################
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
from openerp import api
from openerp.osv import osv, fields
from openerp.tools.translate import _
    
class tapplicant(osv.osv):
    _inherit = 'tapplicant'
    _description = "Trip Applicant"
    _order = "id desc"
    
    _columns = {
                'last_action': fields.char('Last Action'),
                #'property_id': fields.related('trip_id', 'property_id', type="many2one", relation="acesmanpoweruser", string="Property", store=True),
                }
    
    @api.multi
    def write(self, values):
        
        action_dict = {'hasoffersigned':'Offer Signed',
                      'tappforms':'Forms Completed',
                      'unfit':'Pre-Medical Unfit',
                      'medicalpassed':'Pre-Medical Passed',
                      'gamcaunfit':'Gamca Unfit',
                      'gamcapassed':'Gamca Passed',
                      'forremedical':'For Re-medical',
                      'remedicalunfit':'Re-medical Unfit',
                      'remedicalpassed':'Re-medical Passed',
                      'datevisarequested':'Visa Requested',
                      'datevisareceived':'Visa Received',
                      'datevisarenewrequested':'Visa Renewal Requested',
                      'datevisastampembassy':'Submitted To Embassy',
                      'datevisastampreceived':'Visa Stamp Received',
                      'datetraveldocscompleted':'Travel Docs Completed',
                      'dateoecsubmit':'OEC Submitted',
                      'dateoecreceived':'OEC Received',
                      'dateticketrequest':'Ticket Request',
                      'hastravelled':'Joined'}
        
        last_action = [ action_dict[x] for x in values if action_dict.has_key(x) ]
        if last_action:
            values.update({'last_action':last_action[-1]})
        return super(tapplicant, self).write(values)
    
    
    def fetch_data(self, cr, uid, ids,context=None):
        if context is None:
            context = {}
        print "-"*25
        
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        trip_obj = self.pool.get('trip')
        tapplicant_ids = property_ids = []
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
            property_id = manpower_user_obj.browse(cr,uid,property_user_id,context).property_id.id
            # Other Properties
            for obje in manpower_user_obj.browse(cr,uid,property_user_id,context):
                property_ids = [obj.id for obj in obje.property_ids]
            property_ids.append(property_id)
            print "Direct Property ID=",property_id,property_ids
            
        # Find all the candidates who is linked with any of the property
        if property_ids:
            trip_ids = trip_obj.search(cr,uid,[('property_id','in',property_ids)])
            for current_trip_obj in trip_obj.browse(cr,uid,trip_ids,context=context):
                tapplicant_ids.extend([obj.id for obj in current_trip_obj.tapplicant_ids])
                
        domain = [('id','in',tapplicant_ids)]
        flag = self.pool.get('res.users').has_group(cr, uid, 'base.group_marriot_group_property_admin')
        if flag:
            domain = []
        
        print "Domain=",domain
        value = {
                'name': _("Trip Applicants"),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'tapplicant',
                'view_id': False,
                'domain': domain
                }
        print "-"*25
        return value
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

