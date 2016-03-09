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
from openerp import api
from openerp.tools.translate import _


class acesjobseeker(osv.osv):
    _name = 'acesjobseeker'
    _description = "Jobseeker"
    _order = "id desc"
    
    @api.model
    def _needaction_domain_get(self):
        return [('stage_id', '=', 'new')]
    
    _columns = {
            'name': fields.char(size=256, string='Name', required=True, ),
            'email': fields.char(size=100, string='Email', ),
            'mobile': fields.char(size=18, string='Mobile', ),
            'street': fields.char(size=256, string='Street', ),
            'city': fields.char(size=256, string='City', ),
            'country': fields.char(size=256, string='Country', ),
            'stage_id': fields.selection([('new', 'New'),('shortlisted', 'Shortlisted')], 'Status'),
            
            'gender': fields.selection([('male', 'Male'),('female', 'Female')], 'Gender'),
            'nationality': fields.char(size=100, string='Nationality', ),
            'positionpref': fields.char(size=256, string='Position Preferred', ),
            'industrypref': fields.char(size=256, string='Industry Preferred', ),
            'languages': fields.char(size=256, string='Languages', ),
            'dob': fields.date(string='Birthday', ),
            
            'personalinfo': fields.text(string='Personal Info', ),
            'socialinfo': fields.text(string='Social Info', ),
            'experience': fields.text(string='Experience', ),
            'education': fields.text(string='Education', ),
            'skills': fields.text(string='Skills', ),
            'jobsapplied': fields.text(string='Jobs Applied', ),
            'description': fields.text(string='Notes', ),
            
            'expectedsalary':fields.float('Expected Salary'),
            
            'color': fields.integer('Color Index'),
            'user_id': fields.many2one('res.users', 'Responsible', track_visibility='onchange'),
            'url_image': fields.char(size=500, string='Image', ),
            'url_cv': fields.char(size=500, string='CV', ),
            'url_cvpdf': fields.char(size=500, string='CV PDF', ),
            'importid': fields.integer('Import ID'),
            
            'acesmanpowerscreening_ids': fields.one2many('acesmanpowerscreening','acesjobseeker_id','Screening'),
    }
    
    _defaults = {
        'stage_id': 'new',
        'user_id': lambda s, cr, uid, c: uid,
        'color': 0,
    }
    
    @api.multi
    def open_document(self):
        url = self.env.context.get('url')
        action = {
                "type": "ir.actions.act_url",
                "url": url,
                "target":"new",
            }
        return action
