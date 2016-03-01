from openerp.osv import osv, fields
from openerp import tools
from openerp.modules.module import get_module_resource


class acesmanpoweruser(osv.osv):
    _name = 'acesmanpoweruser'
    _description = "Recruitment Users"
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, ids, name, value, args, context=None):
        if value:
            return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
        return True
    
    
    _columns = {
    
        'name': fields.char(size=256, string='Name', required=True, ),
        'username': fields.char(size=256, string='Username',  ),
        'password': fields.char(size=256, string='Password', required=True, ),
        
        'access_id': fields.selection([('staff', 'Recruitment Staff'),('manager','Manager'),('admin','Administrator')], 'Role / Access Level'),
        'email': fields.char(size=100, string='Email', required=True ),
        'mobile': fields.char(size=100, string='Mobile', required=True),
        
        'company_id': fields.many2one('res.company', 'Company Group', required=True),
        'user_id': fields.many2one('res.users', 'Related User'),
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by', readonly=True),
        'description': fields.text(string='Notes', ),
        
        'property_id': fields.many2one('acesmanpowerproperty', 'Property', required=True),
        'property_ids': fields.one2many('acesmanpowerproperty','acesmanpoweruser_id','Other Properties'),
        
        'acesmanpowerevent_ids': fields.one2many('acesmanpowerevent','acesmanpoweruser_id','Recruitment Event'),
        
        
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Photo",
            help="This field holds the image used as photo for the applicant, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized photo", type="binary", multi="_get_image",
            store = {
                'acesmanpoweruser': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized photo of the employee. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized photo", type="binary", multi="_get_image",
            store = {
                'acesmanpoweruser': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized photo of the employee. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
                 
    }
    
    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))
        
    _defaults = {
        'image': _get_default_image,
        'access_id': 'staff',
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
        
    }
    
    def onchange_email(self, cr, uid, ids, email, username, context = None):
        values = {'username': '' }
        if email or '':
            email = email.strip(' \t\n\r')
        if username == '':
            values['username'] = email
            
        return {'value': values}
    
    
    
    
class res_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    _columns = {
        'acesmanpoweruser_id': fields.many2one('acesmanpoweruser', 'Recruitment User'),
        
    }
    
    
    
    
    