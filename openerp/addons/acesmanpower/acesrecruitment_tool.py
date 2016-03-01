from openerp.osv import osv, fields


class cv_dropbox(osv.osv):
    _name = 'cv.dropbox'
    _description = "CV Dropbox"
    _order = "id desc" 
    
    _columns = {
                'name' : fields.char("Name")
                }
    
class cv_byemail(osv.osv):
    _name = 'cv.byemail'
    _description = "CV Rceived by email"
    _order = "id desc" 
    
    _columns = {
                'name' : fields.char("Name")
                }
    
class job_position(osv.osv):
    _name = 'job.position'
    _description = "job Position"
    _order = "id desc" 
    _columns ={
               'name' : fields.char("Name")
               }
    
class job_industry(osv.osv):
    _name = 'job.industry'
    _description = "Job Industry"
    _order = "id desc" 
    _columns ={
               'name' : fields.char("Name")
               }
    
class job_posting(osv.osv):
    _name = 'job.posting'
    _description = "Job Posting"
    _order = "id desc" 
    
    _columns = {
                'posting_intro': fields.char("Posting Introduction"),
                'posting_title':fields.char("Post Title"),
                'name' : fields.char("Name"),
                'url_image': fields.char(size=500, string='Choose Page URL'),
                'recruit_date':fields.date("Recruit Date"),
                'job_locations':fields.many2many('res.country','res_country_rel','job_location_id','country_id',"Job Locations"),
                'recruit_locations':fields.many2many('res.country','res_recruitment_country_rel','recruit_location_id','country_id',"Recruitment Location"),
                'jobs':fields.many2many('job.position','job_position_rel','job_id','job_position_id',"Jobs"),
                'job_industry':fields.many2many('job.industry','job_industry_rel','job_id','industry_id',"Industry"),
                'job_details':fields.text("Details"),
                'publish':fields.boolean("Unpublished Avert")
                }