from openerp.osv import osv, fields


class acesmanpowerjob(osv.osv):
    _name = 'acesmanpowerjob'
    _description = "Job"
    _order = "name asc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']


    _columns = {
        'name': fields.char(size=256, string='Job Title', required=True, ),
        'quantity': fields.integer('Quantity'),
        'jobdescription': fields.text(string='Job Description', ),
        'qualification': fields.text(string='Qualifications', ),
        
        'acesmanpoweruser_id': fields.many2one('acesmanpoweruser', 'Owner', track_visibility='onchange'),
        'acesmanpowerproperty_id': fields.many2one('acesmanpowerproperty', 'Property'),
        'acesmanpowerevent_id': fields.many2one('acesmanpowerevent', 'Recruitment Event'),
        
        #'acesmanpowerproperty_id': fields.related('acesmanpowerjob_id', 'acesmanpowerproperty_id', type="many2one", relation="acesmanpowerproperty", string="Property", store=True),
        
        'company_id': fields.many2one('res.company', 'Company', readonly=True),
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
        'user_id': fields.many2one('res.users', 'Updated by', readonly=True),
        
    }
    
    
    _defaults = {
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
        'acesmanpoweruser_id': lambda self, cr, uid, c: c.get('acesmanpoweruser_id', False),
        'user_id': lambda s, cr, uid, c: uid,
    }
    
    
    

    
    
    
    
    
    
    