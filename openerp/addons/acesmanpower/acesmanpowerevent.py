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
import urllib

from openerp import api
from openerp.osv import osv, fields

class acesmanpowerevent(osv.osv):
    _name = 'acesmanpowerevent'
    _description = "Recruitment Event"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    @api.v8
    def getdefaultpartner(self):
        return True
    
    @api.v8
    def get_urlencode(self, f1='a', v1='1', f2='b', v2='2', f3='c', v3='3'):
        f = { f1 : v1, f2 : v2, f3 : v3}
        return urllib.urlencode(f)
    
    @api.v8
    def get_quote(self, text):
        return urllib.quote(text)
    
    def getbase64(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        users = self.pool.get('res.users').browse(cr, uid, [uid])
        
        for w in self.browse(cr, uid, ids, context=context):
            for r in users:
                result[w.id] = base64.b64encode((str(uid) or '') + '---' + r.password)
        
        return result
    
    @api.multi
    def action_view_invite(self):
        return True
    
    @api.multi
    def action_view_participant(self):
        return True
    
    @api.multi
    def action_view_registration(self):
        return True
    
    @api.multi
    def action_view_shortlists(self):
        return True
    

    _columns = {
            'name': fields.char(size=256, string='Name', required=True, ),
            'email': fields.char(size=100, string='Email', ),
            'mobile': fields.char(size=100, string='Mobile', ),
            'street': fields.char(size=256, string='Street', ),
            'city': fields.char(size=256, string='City', ),
            'can_country_id': fields.many2one('res.country', 'Recruit Location'),
            
            'stage_id': fields.selection([('new', 'New'),('approved', 'Approved'),('disapproved','Disapproved'),('done','Done'),('cancelled','Cancelled')], 'Status', track_visibility='onchange' ),
            'company_id': fields.many2one('res.company', 'Company'),
            'user_id': fields.many2one('res.users', 'Created User', readonly=True, ),
            'acesmanpoweruser_id': fields.related('user_id', 'acesmanpoweruser_id', type="many2one", relation="acesmanpoweruser", string="Recruitment User", store=True),
            'partner_id': fields.related('user_id', 'partner_id', type="many2one", relation="res.partner", string="Contact Person", store=True),
            
            'email': fields.related('user_id', 'email', type='char', size=256, string='Email', store=True),
            'mobile': fields.related('user_id', 'mobile', type='char', size=256, string='Mobile', store=True),
            'secu': fields.related('user_id', 'password', type='char', size=256, string='****', store=True, readonly=True),
            
            'datestart': fields.date(string='Start', ),
            'dateend': fields.date(string='End', ),
            
            'twitterhashtag': fields.char(size=100, string='Twitter Hash Tag', ),
            'color': fields.integer('Color Index'),
            'url_image': fields.char(size=500, string='Image url', ),
            'description': fields.text(string='Notes', ),
            
            'hr_job_ids': fields.many2many('hr.job','hr_job_acesmanpowerevent_rel', 'acesmanpowerevent_id', 'hr_job_id'),
            'acesmanpowerjob_ids': fields.one2many('acesmanpowerjob','acesmanpowerevent_id','Jobs'),
            
            'acesmanpowerproperty_ids': fields.many2many('acesmanpowerproperty','acesmproperty_acesmevent_rel', 'acesmanpowerevent_id', 'acesmanpowerproperty_id', string="Properties"),
            
            'create_date': fields.datetime('Create Date', readonly=True),
            'write_date': fields.datetime('Updated', readonly=True),
            'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
            
            'getbase64enc' : fields.function(getbase64, method=True, string='Secure', type='char', size=500, readonly=True),
            
    }
    
    _defaults = {
        'stage_id': 'new',
        'user_id': lambda s, cr, uid, c: uid,
        'color': 0,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
    }
    
    _order = "id desc"
    
class hr_job(osv.osv):
    _name = "hr.job"
    _inherit = "hr.job"
    _columns = {
        'acesmanpowerevent_ids': fields.many2many('acesmanpowerevent', 'hr_job_acesmanpowerevent_rel', 'hr_job_id', 'acesmanpowerevent_id'),
    }

class hr_employee(osv.osv):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _columns = {
        'company_id': fields.many2one('res.company', 'Company'),
    }
    
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
    }

