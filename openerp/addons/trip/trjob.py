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
from openerp.osv import osv, fields
from datetime import datetime
from openerp import tools
from openerp.modules.module import get_module_resource

from dateutil.relativedelta import relativedelta



class trjob(osv.osv):
    _name = 'trjob'
    _description = "Trip Jobs"
    _order = 'name asc'
    
    
    
    def _candidatesplaced(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
          result[r.id] = len(r.tapplicant_id)
        
        return result

        
    def compute_balancepercent(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
          if  r.candidatesrequired:
            result[r.id] = (len(r.tapplicant_id) * 100) / r.candidatesrequired
          else:
            result[r.id] = 0
        
        return result
        
        

    _columns = {
        'name': fields.char(size=256, string='Name', ),
        'description': fields.text(string='Description'  ),
        'candidatesrequired': fields.integer('Amount Required'),
        'candidatesplaced' : fields.function(_candidatesplaced, method=True, string='Total Placed', type='integer', store=True, readonly=True),
        'trip_id': fields.many2one('trip', 'Trip'),
        'partner_id': fields.related('trip_id', 'partner_id', type="many2one", relation="res.partner", string="Employer", readonly=True),
        'user_id': fields.many2one('res.users', 'Responsible', track_visibility='onchange'),
        'company_id': fields.many2one('res.company', 'Branch'),
        
        'tapplicant_id': fields.one2many('tapplicant', 'trjob_id', 'Applicants Placed', store=True),
        'placedpercent' : fields.function(compute_balancepercent, method=True, string='Placed Percent', type='float', readonly=True),
    }
    
    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
    }
    
    _sql_constraints = [
        ('tripjob_unique', 'unique(name,trip_id)', 'Job already exists in this Trip!')
    ]


    
trjob()