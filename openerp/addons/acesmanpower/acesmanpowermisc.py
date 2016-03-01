from openerp.osv import osv, fields

class acesmanpowerjob(osv.osv):
    _name = 'acesmanpowerjob'
    _description = "the Jobs"

    _columns = {
            'name': fields.char(size=256, string='Name', required=True, ),
            'email': fields.char(size=100, string='Email', ),
            'mobile': fields.char(size=100, string='Mobile', ),
            'street': fields.char(size=256, string='Street', ),
            'city': fields.char(size=256, string='City', ),
            'country': fields.char(size=256, string='Country', ),
            
            'stage_id': fields.selection([('new', 'New'),('approved', 'Approved'),('confirmed','Confirmed'),('done','Done'),('cancelled','Cancelled')], 'Status'),
            'branch_id': fields.many2one('res.company', 'Branch'),
            'user_id': fields.many2one('res.users', 'Organizer', track_visibility='onchange'),
            
            'datestart': fields.date(string='Start', ),
            'dateend': fields.date(string='End', ),
            
            'twitterhashtag': fields.char(size=100, string='Twitter Hash Tag', ),
            'color': fields.integer('Color Index'),
            'url_image': fields.char(size=500, string='Image', ),
            
            #'partner_ids': fields.many2many('res.partner', 'acesevent_id', string='Employers' ),
            #'ajapplicant_ids': fields.many2many('acesjobseeker','aevent_ajos_rel','acesevent_id','ajobseeker_id',string='Applicants'),
            
            
            
    }
    
    _defaults = {
        'stage_id': 'new',
        'user_id': lambda s, cr, uid, c: uid,
        'color': 0,
    }
    

acesmanpowerjob()


