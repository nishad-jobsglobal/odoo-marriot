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
import psycopg2
import requests
import json
import re
import datetime

from openerp import api
from openerp.osv import osv, fields
from openerp.tools.translate import _

class acesjobseeker(osv.osv):
    _name = 'acesjobseeker'
    _description = "Jobseeker"
    _order = "id desc"
    
    @api.model
    def _needaction_domain_get(self):
        return [('stage_id', '=', 'new')]
    
    def fetch_data(self, cr, uid, ids, stage=None, context=None):
        if context is None:
            context = {}
        print "-"*25
        
        manpower_user_obj = self.pool.get('acesmanpoweruser')
        # Find the log in user and his related property user id
        if manpower_user_obj.search(cr,uid,[('user_id','=',uid)]):
            log_in_user = uid
            property_user_id = manpower_user_obj.search(cr,uid,[('user_id','=',uid)])
            print "Log In user {'%s'} = Property User {'%s'}"%(log_in_user,property_user_id[0])
        else:
            pass
        
        domain = [('for_marriot','=',True)]
        value = {
                'name': _('CV Search'),
                'view_type': 'form',
                'view_mode': 'tree,form',
                'type': 'ir.actions.act_window',
                'res_model': 'acesjobseeker',
                'view_id': False,
                'domain': domain
                }
        print "-"*25
        return value
    
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
            'company_id': fields.many2one('res.company', 'Company'),
            'url_image': fields.char(size=500, string='Image', ),
            'url_cv': fields.char(size=500, string='CV', ),
            'url_cvpdf': fields.char(size=500, string='CV PDF', ),
            'url_profile': fields.char(size=500, string='Profile URL', ),
            'importid': fields.integer('Import ID'),
            'for_marriot': fields.boolean('For Marriot'),
            'shortlist_tags':fields.many2many('shortlist.tags','shortlist_tags_rel','jobseeker_id','tag_id',"Tag your Shortlists"),
            
            'acesmanpowerscreening_ids': fields.one2many('acesmanpowerscreening','acesjobseeker_id','Screening'),
    }
    
    _defaults = {
        'stage_id': 'new',
        'user_id': lambda s, cr, uid, c: uid,
        'company_id': lambda self, cr, uid, ctx=None: self.pool.get('res.company')._company_default_get(cr, uid, 'acesjobseeker', context=ctx),
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
    
    def _fetch_jobseeker_image(self,dbdata):
        if not dbdata:
            return ""
        file_no = int(dbdata.split('.')[0])
        file_ext = dbdata.split('.')[1]
        if file_no < 10001:
            folder_range = '0to10'
        elif file_no > 10000 and file_no < 20001:
            folder_range = '10to20'
        elif file_no > 20000 and file_no < 30001:
            folder_range = '20to30'
        elif file_no > 30000 and file_no < 40001:
            folder_range = '30to40'
        elif file_no > 40000 and file_no < 50001:
            folder_range = '40to50'
        elif file_no > 50000 and file_no < 60001:
            folder_range = '50to60'
        elif file_no > 60000 and file_no < 90001:
            folder_range = '60to80'
        elif file_no > 90000 and file_no < 99999:
            folder_range = '80to100'
        else:
            folder_range = ''
        formated_data = "http://jobsglobal.com/company/media_pp_all/"+ folder_range + "/" + str(file_no)+'.'+file_ext
        return formated_data
    
    def _get_profile_url(self,dbdata):
        formated_data = ''
        if not dbdata:
            return formated_data
        formated_data = "http://www.jobsglobal.com/profile/%s"%(str(dbdata))
        return formated_data
    
    def _get_nationality(self,dbdata):
        formated_data = ''
        if not dbdata:
            return formated_data
        country = requests.get("http://jobsglobal.com/_webservice/cp/api/v1/country/%s"%(str(dbdata)))
        country_data = json.loads(country.text)
        formated_data = country_data['name']
        return formated_data
    
    def _format_data(self,cr,uid,ids,key,dbdata):
        
        formated_data = ''
        if not dbdata:
            return formated_data
        
        final = dbdata.encode('ascii','ignore')
        if not final.endswith("}"):
            final = final.split('|')
            final = final[:-1]
        else:
            final = final.split('|')
            
        if key == 'skills':
            formated_data = dbdata.encode('ascii','ignore').replace('|',',')
            
        elif key == 'experience':
            exp_data = ''
            exp_vals = [('position','Position'),('company','Company'),
                  ('jobdetail','Job Details'),('jobplaintext','Desc'),
                  ('jobstart','Start'),('jobend','End')]
            exp_data = ""
            for item in final:
                try:
                    item = json.loads(item)
                except ValueError:
                    continue
                for i in exp_vals:
                    exp_data += i[1] + ':' + re.sub(r'\s+', ' ', item[i[0]]) + '\n'
                exp_data += '--------------------------------\n'
            formated_data = exp_data
            
        elif key == 'education':
            edu_vals = [('course','Course'),('school','School'),
                        ('plaintext','Description'),('datec','Date Completed')]
            edu_data = ""
            for item in final:
                try:
                    item = json.loads(item)
                except ValueError:
                    continue
                for i in edu_vals:
                    edu_data += i[1] + ':' + re.sub(r'\s+', ' ', item[i[0]]) + '\n'
                edu_data += '--------------------------------\n'
            formated_data = edu_data
            
        elif key == 'personalinfo':
            per_vals = [('pi_height','Height'),('pi_weight','Weight'),('pi_complexion','Complexion'),
                        ('pi_maritalstatus','Status'),('pi_visastatus','Visa Status'),('pi_availability','Availability')]
            personal_data = ""
            for item in final:
                try:
                    item = json.loads(item)
                except ValueError:
                    continue
                for i in per_vals:
                    personal_data += i[1] + ':' + re.sub(r'\s+', ' ', item[i[0]]) + '\n'
                personal_data += '--------------------------------\n'
            formated_data = personal_data
            
        elif key == 'positionpreferred':
            formated_data = dbdata.encode('ascii','ignore').replace('|',',')
        else:
            formated_data = ''
        return formated_data
    
    def format_jobseeker_data(self,cr,uid,jobseeker_id,context=None):
        
        if not jobseeker_id:
            return True
        cr.execute(""" SELECT datecreate,personalinfo,education,language,industrypreferred,
                                 positionpreferred,email,birthdate,nationality,name,phone1,experience,
                                 skills,gender,socialinfo,locationcurrent_city,odoo_user_id,odoo_company_id,
                                 url,photofilename FROM jobseeker WHERE idjobseeker='%s' """%(jobseeker_id))
        rst = cr.fetchone()
        try:
            if rst not in (None,[],[None]):
                create_date = datetime.datetime.strptime(rst[0], "%Y-%m-%d %H:%M:%S")
                personalinfo = self._format_data(self,cr,uid,'personalinfo',rst[1])
                education = self._format_data(self,cr,uid,'education',rst[2])
                language = rst[3] or ''
                industrypreferred = rst[4] or ''
                positionpreferred = self._format_data(self,cr,uid,'positionpreferred',rst[5])
                email = rst[6] or ''
                birthdate = datetime.datetime.strptime(rst[7], "%Y-%m-%d")
                nationality = self._get_nationality(rst[8])
                name = rst[9] or ''
                phone1 = rst[10] or ''
                experience = self._format_data(self,cr,uid,'experience',rst[11])
                skills = self._format_data(self,cr,uid,'skills',rst[12])
                gender = rst[13]
                socialinfo = rst[14] or ''
                city = rst[15] or ''
                user_id = rst[16]
                company_id = rst[17]
                stage_id = 'new'
                url_riginal_cv = "http://jobsglobal.com/company/controlpanel/ray/getfile.php?id=%s"%(str(jobseeker_id))
                url_cv_pdf = "http://www.jobsglobal.com/company/controlpanel/ray/pdfprofile/create.profile.to.pdf.2.php?id=%s"%(str(jobseeker_id))
                importid = int(jobseeker_id)
                url_profile = self._get_profile_url(rst[18])
                photofilename = self._fetch_jobseeker_image(rst[19])
                
                cr.execute(""" INSERT INTO acesjobseeker 
                         (  
                            create_date,
                            personalinfo,
                            education,
                            languages,
                            industrypref,
                            positionpref,
                            email,
                            dob,
                            nationality,
                            name,
                            mobile,
                            experience,
                            skills,
                            gender,
                            socialinfo,
                            city,
                            stage_id,
                            for_marriot,
                            user_id,
                            company_id,
                            create_uid,
                            write_uid,
                            write_date,
                            url_cv,
                            url_cvpdf,
                            importid,
                            url_profile,
                            url_image
                            )
                        VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s',
                                '%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s'
                                ) """%(create_date,personalinfo,education,language,industrypreferred,
                                       positionpreferred,email,birthdate,nationality,name,phone1,
                                       experience,skills,gender,socialinfo,city,stage_id,True,user_id,
                                       company_id,user_id,user_id,create_date,url_riginal_cv,url_cv_pdf,
                                       importid,url_profile,photofilename))
        except:
            pass
        return True   
           
    
class shortlist_tags(osv.osv):
    
    _name = 'shortlist.tags'
    _description = "Tag your shortlists"
    _order = "id desc"
    
    _columns = {
                'name':fields.char('Name'),
                }
    
