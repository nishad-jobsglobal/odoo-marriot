from openerp.osv import osv, fields
from openerp import api

class acesmanpowerscreening(osv.osv):
    _name = 'acesmanpowerscreening'
    _description = "Recruitment Screening"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    @api.model
    def _needaction_domain_get(self):
        return [('state_id', '=', 'new')]

    _columns = {
        'acesjobseeker_id': fields.many2one('acesjobseeker', 'Jobseeker', required=True),
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
    
