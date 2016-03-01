# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
from datetime import datetime
from openerp import tools
from openerp.modules.module import get_module_resource

#from openerp import models, fields, api


from dateutil.relativedelta import relativedelta


class mkjosms(osv.osv):
    _name = 'mkjosms'
    _columns = {
        'name' : fields.char('Name', required=True),
        'stage_id' : fields.selection((('draft', 'Draft'), ('queued', 'Queued'), ('done', 'Done')), 'Stage'),
        'message' : fields.text('Message'),
        'boximport' : fields.text('Recipients'),
        'tapplicant_ids' : fields.many2many('tapplicant', 'mkjosms_tappliant_rel','mkjosms_id','tapplicant_id', 'Recipients', domain="[('mobile','=',True)]"),
        'create_date' : fields.datetime('Create Date', readonly=True),
        'write_date' : fields.datetime('Updated', readonly=True),
        'write_uid' : fields.many2one('res.users', 'Updated by', readonly=True),
        'user_id' : fields.many2one('res.users', 'Responsible'),
        'company_id' : fields.many2one('res.company', 'Branch'),
    }
    
    
    _defaults = {
        
        'user_id': lambda s, cr, uid, c: uid,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
    }
    
    
mkjosms() 


    
    
class tapplog(osv.osv):
    _name = 'tapplog'
    _columns = {
        'name' : fields.char('Name', required=True),
        'description' : fields.text('Description'),
        'tapplicant_id': fields.many2one('tapplicant', 'Applicant'),
        'create_date' : fields.datetime('Create Date', readonly=True),
        'write_date' : fields.datetime('Updated', readonly=True),
        'write_uid' : fields.many2one('res.users', 'Updated by', readonly=True),
        'user_id' : fields.many2one('res.users', 'Responsible'),
        'company_id' : fields.many2one('res.company', 'Branch'),
    }
    
    
    _defaults = {
        
        'user_id': lambda s, cr, uid, c: uid,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
    }
    
    
      
tapplog() 