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



class tapplicant_stage(osv.osv):
    """ Stage of Applicant """
    _name = "tapplicant.stage"
    _description = "Stage of Applicant"
    _order = 'sequence'
    _columns = {
        'name': fields.char('Name', size=256, required=True, translate=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of stages."),        
        'template_id': fields.many2one('email.template', 'Use template', help="If set, a message is posted on the processor when the applicant is set to the stage."),
        'fold': fields.boolean('Folded in Kanban View',
                               help='This stage is folded in the kanban view when'
                               'there are no records in that stage to display.'),
    }
    _defaults = {
        'sequence': 1,
    }



class tapplicant(osv.osv):
    _name = 'tapplicant'
    _description = "Trip Applicant"
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)
    
    def compute_t_age(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        now = datetime.now()
        for r in self.browse(cr, uid, ids, context=context):
          if r.date_birth:
            dob = datetime.strptime(r.date_birth,'%Y-%m-%d')
            delta=relativedelta (now, dob)
            result[r.id] = str(delta.years) +" years, "+ str(delta.months) +" months " #if you only want date just give delta.years
          else:
            result[r.id] = "No Date of birth!"
        return result
        
    def isexpiredmed(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        now = datetime.now()
        for r in self.browse(cr, uid, ids, context=context):
          if r.datemedicalexpire:
            dob = datetime.strptime(r.datemedicalexpire,'%Y-%m-%d')
            delta = dob - now
            
            if delta.days > 0:
                result[r.id] = str(delta.days) +" days"
            else:
                result[r.id] = "Expired!"
          else:
                result[r.id] = ""
        return result

    def isexpiredgamca(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        now = datetime.now()
        for r in self.browse(cr, uid, ids, context=context):
          if r.dategamcaexpire:
            dob = datetime.strptime(r.dategamcaexpire,'%Y-%m-%d')
            delta = dob - now
            
            if delta.days > 0:
                result[r.id] = str(delta.days) +" days"
            else:
                result[r.id] = "Expired!"
          else:
                result[r.id] = ""
        return result        
        
    def isexpiredremed(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        now = datetime.now()
        for r in self.browse(cr, uid, ids, context=context):
          if r.dateremedicalexpire:
            dob = datetime.strptime(r.dateremedicalexpire,'%Y-%m-%d')
            delta = dob - now
            
            if delta.days > 0:
                result[r.id] = str(delta.days) +" days"
            else:
                result[r.id] = "Expired!"
          else:
                result[r.id] = ""
        return result        
        
    def isexpiredvisa(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        now = datetime.now()
        for r in self.browse(cr, uid, ids, context=context):
          if r.datevisaexpire:
            dob = datetime.strptime(r.datevisaexpire,'%Y-%m-%d')
            delta = dob - now
            
            if delta.days > 0:
                result[r.id] = str(delta.days) +" days"
            else:
                result[r.id] = "Expired!"
          else:
                result[r.id] = ""
        return result        
        
        
        
        
    def _get_default_stage_id(self, cr, uid, context=None):
        search_domain = []
        search_domain.append(('name', '=', 'Profiling'))
        # perform search, return the first found
        stage_ids = self.pool.get('tapplicant.stage').search(cr, uid, search_domain, context=context)
        if stage_ids:
            return stage_ids[0]
        return False
    
    
    def compute_totalfee(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
          if r.feeplacement or r.feeprocessing:
            result[r.id] = r.feeplacement + r.feeprocessing
          else:
            result[r.id] = 0
        
        return result

    def compute_totalcollected(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
          if r.collplacement or r.collprocessing:
            result[r.id] = r.collplacement + r.collprocessing
          else:
            result[r.id] = 0
        
        return result

    def compute_amountbalance(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
          if r.feeplacement or r.feeprocessing or r.collplacement or r.collprocessing:
            result[r.id] = r.feeplacement + r.feeprocessing - r.collplacement - r.collprocessing
          else:
            result[r.id] = 0
        
        return result

    def compute_balancepercent(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
          if  r.feeplacement or r.feeprocessing:
            result[r.id] = ((r.collplacement + r.collprocessing) * 100) / (r.feeplacement + r.feeprocessing)
          else:
            result[r.id] = 0
        
        return result

    def compute_totalexpenses(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
          if r.expenseoec or r.expenseinsurance or r.expensestamping or r.expensetranslation or r.expensemedical or r.expenseetc:
            result[r.id] = r.expenseoec + r.expenseinsurance + r.expensestamping + r.expensetranslation + r.expensemedical + r.expenseetc
          else:
            result[r.id] = 0
        
        return result

    
    
    # Defining tracking here
    
    def _frprflng(self, cr, uid, ids, fields, arg, context):
        result = {}
        for r in self.browse(cr, uid, ids, context=context):
            result[r.id] = (str(r.reds).find('frprflng') + 1)
        return result
    
    
    _columns = {
        'name': fields.char(size=256, string='Name', required=True, ),
        'user_email': fields.char(size=256, string='Email', write=['hr']),
        'phone': fields.char('Phone', size=64),
        'mobile': fields.char('Mobile', size=64),
        'date_birth': fields.date('Birthdate'),
        'gender': fields.selection([('male', 'Male'),('female', 'Female')], 'Gender'),
        'homeaddress': fields.char('Home Address', size=256),
        'salary_basic': fields.float('Basic Salary', help="Basic Salary Offered by the Employer"),
        'salary_gross': fields.float('Gross Salary', help="Gross Salary Offered by the Employer"),
        
        'age' : fields.function(compute_t_age, method=True, string='Age', type='char', size=32, readonly=True),
        
        'medicalclinic': fields.char('Medical Clinic', size=256),
        
        # Document Collection
        'hascv': fields.boolean('CV Attached'),
        'hasinterviewsheet': fields.boolean('Interview Sheet Attached'),
        'haspassport': fields.boolean('Passport Attached'),
        'hasoffersigned': fields.boolean('Offer Signed'),
        'hasphoto': fields.boolean('Photo Attached'),
        'formscompleted': fields.boolean('Forms Completed'),
        
        'nationality': fields.many2one('res.country', 'Nationality', store=False),
        'passportnumber': fields.char('Passport Number', size=64),
        'passportnotes': fields.char('Passport Notes', size=256),
        'passportexpiry': fields.date('Passport Expiry'),
        
        'tappforms': fields.many2many('trip_form', 'tapp_trifor_rel', 'tapp_id', 'trip_form_id', string='Forms'),
        'dateformscompleted': fields.date('Forms Completed On'),
        
        # Medical Processing
        
        'medicalnotneeded': fields.boolean('Pre-Medical not needed'),
        'unfit': fields.boolean('Pre-Medical Unfit'),
        'medicalpassed': fields.boolean('Pre-Medical Passed'),
        'datemedicalstart': fields.date('Medical Test Started'),
        'datemedicalfit': fields.date('Medically Fit'),
        'datemedicaluploaded': fields.date('Medical Uploaded'),
        'datemedicalexpire': fields.date('Medical Expiry'),
        'medicalexpirenote' : fields.function(isexpiredmed, method=True, string='Medical Expiring In', type='char', size=64, readonly=True),
        
        'gamcanotneeded': fields.boolean('Gamca not needed'),
        'mofanotneeded': fields.boolean('Mofa not needed'),
        'gamcaunfit': fields.boolean('Gamca Unfit'),
        'gamcapassed': fields.boolean('Gamca Passed'),
        'dategamcastart': fields.date('Gamca Test Started'),
        'dategamcafit': fields.date('Gamca Fit'),
        'dategamcauploaded': fields.date('Gamca Uploaded'),
        'datemofauploaded': fields.date('Mofa Uploaded'),
        'dategamcaexpire': fields.date('Gamca Expiry'),
        'gamcaexpirenote' : fields.function(isexpiredgamca, method=True, string='Gamca Expiring In', type='char', size=64, readonly=True),
        
        'forremedical': fields.boolean('For Re-medical'),
        'remedicalunfit': fields.boolean('Re-medical Unfit'),
        'remedicalpassed': fields.boolean('Re-medical Passed'),
        'dateremedicalstart': fields.date('Re-medical Test Started'),
        'dateremedicalfit': fields.date('Re-medically Fit'),
        'dateremedicaluploaded': fields.date('Re-medical Uploaded'),
        'dateremedicalexpire': fields.date('Re-medical Expiry'),
        'remedicalexpirenote' : fields.function(isexpiredremed, method=True, string='Re-medical Expiring In', type='char', size=64, readonly=True),
        
        'medicalnote': fields.char('Medical Note', size=256),
        
        'dateendorsedvisa': fields.date('Endorsed for Visa'),
        'datevisarequested': fields.date('Visa Requested'),
        'datevisareceived': fields.date('Visa Recieved'),
        'datevisaexpire': fields.date('Visa Expiry'),
        'visaexpirenote' : fields.function(isexpiredvisa, method=True, string='Visa Expiring In', type='char', size=64, readonly=True),
        
        'gamcaclinic': fields.char('Medical Clinic', size=256),
        
        'datenbi': fields.date('NBI/PCC Recieved'),
        'dateendorsedvisastamp': fields.date('Endorsed Visa Stamp'),
        'dateclearedvisastamp': fields.date('Cleared For Visa Stamp'),
        'datevisastampembassy': fields.date('Submitted To Embassy'),
        'datevisastampreceived': fields.date('Visa Stamp Recieved'),
        
        'dateendorsedvisarenew': fields.date('Endorsed for Visa Renewal'),
        'datevisarenewrequested': fields.date('Visa Renewal Requested'),
        
        'isstarttravelprocess': fields.boolean('Start Travel Processing'),
        'visanote': fields.char('Visa Note', size=256),
        
        'datetravelproccleared': fields.date('Cleared Travel Processing'),
        'dateoecsubmit': fields.date('OEC Submitted'),
        'dateoecreceieved': fields.date('OEC Received'),
        'dateoecexpire': fields.date('OEC Expire'),
        'dateinsurancereceived': fields.date('Insurance Received'),
        'tapptraveldocs': fields.many2many('trip_traveldoc', 'tapp_travdoc_rel', 'trdocapp_id', 'trip_traveldoc_id', string='Travel Documents'),
        'datetraveldocscompleted': fields.date('Travel Docs Completed'),
        
        'dateticketrequest': fields.date('Ticket Request'),
        'dateticketissueclear': fields.date('Cleared For Ticket'),
        'datetravel': fields.date('Travel Date'),
        'flightdetails': fields.char('Flight Details', size=256),
        'hastravelled': fields.boolean('Has Travelled'),
        
        
        'feeplacement': fields.float('Placement'),
        'feeprocessing': fields.float('Processing'),
        'totalfee' : fields.function(compute_totalfee, method=True, string='Total Fees', type='float', readonly=True),
        
        'collplacement': fields.float('Placement'),
        'collprocessing': fields.float('Processing'),
        'totalcollected' : fields.function(compute_totalcollected, method=True, string='Total Collected', type='float', readonly=True),
        'amountbalance' : fields.function(compute_amountbalance, method=True, string='Balance', type='float', readonly=True),
        'balancepercent' : fields.function(compute_balancepercent, method=True, string='Balance Percent', type='float', readonly=True),
        
        'expenseoec': fields.float('OEC'),
        'expenseinsurance': fields.float('Insurance'),
        'expensestamping': fields.float('Visa Stamping'),
        'expensetranslation': fields.float('Visa Translation'),
        'expensemedical': fields.float('Medical'),
        'expenseetc': fields.float('Other Expenses'),
        'totalexpenses' : fields.function(compute_totalexpenses, method=True, string='Total Expenses', type='float', readonly=True),
        
        'expenseoecdate': fields.date('Date OEC'),
        'expenseinsurancedate': fields.date('Date Insurance'),
        'expensestampingdate': fields.date('Date Visa Stamping'),
        'expensetranslationdate': fields.date('Date Visa Translation'),
        'expensemedicaldate': fields.date('Date Medical'),
        'expenseetcdate': fields.date('Date Other Expenses'),
        'expenseetcnote': fields.char('Expense Details', size=256),
        
        
        'active': fields.boolean('Active',),
        'color': fields.integer('Color Index'),
        'company_id': fields.many2one('res.company', 'Branch'),
        'description': fields.text('Description'),
        'stage_id': fields.many2one ('tapplicant.stage', 'Stage', track_visibility='onchange'),
        
        'user_id': fields.many2one('res.users', 'Responsible', track_visibility='onchange'),
        'date_closed': fields.datetime('Closed', readonly=True, select=True),
        'date_open': fields.datetime('Assigned', readonly=True, select=True),
        'date_last_stage_update': fields.datetime('Last Stage Update', select=True),
        'date_action': fields.date('Next Action Date'),
        'title_action': fields.char('Next Action', size=128),
        
        'trip_id': fields.many2one('trip','Recruitment Trip'),
        'partner_id': fields.related('trip_id', 'partner_id', type="many2one", relation="res.partner", string="Employer", store=True),
        
        
        
        'frprflng': fields.integer('frprflng'),
        'tpdtchrgs': fields.integer('tpdtchrgs'),
        'frdcmntcllctn': fields.integer('frdcmntcllctn'),
        'frmdcltst': fields.integer('frmdcltst'),
        'mdclnprcss': fields.integer('mdclnprcss'),
        'fttwrk': fields.integer('fttwrk'),
        'frmdclpld': fields.integer('frmdclpld'),
        'frgmctst': fields.integer('frgmctst'),
        'gmcnprcss': fields.integer('gmcnprcss'),
        'gmcfttwrk': fields.integer('gmcfttwrk'),
        'frgmcpld': fields.integer('frgmcpld'),
        'wtngmf': fields.integer('wtngmf'),
        'frvsrqst': fields.integer('frvsrqst'),
        'wtngvsrls': fields.integer('wtngvsrls'),
        'nhldfrblncpymnts': fields.integer('nhldfrblncpymnts'),
        'nhldfrnncprtn': fields.integer('nhldfrnncprtn'),
        'ndrsdfrhclrnc': fields.integer('ndrsdfrhclrnc'),
        'vsxprd': fields.integer('vsxprd'),
        'vsrnwlnprcss': fields.integer('vsrnwlnprcss'),
        'wtngvsrnwlrls': fields.integer('wtngvsrnwlrls'),
        'mdclxprd': fields.integer('mdclxprd'),
        'frrmdcltst': fields.integer('frrmdcltst'),
        'wtngrmdclrls': fields.integer('wtngrmdclrls'),
        'ndrsdfrvsstmpng': fields.integer('ndrsdfrvsstmpng'),
        'clrdfrvsstmpng': fields.integer('clrdfrvsstmpng'),
        'vsstmpngnprcss': fields.integer('vsstmpngnprcss'),
        'wtngvsstmpngrls': fields.integer('wtngvsstmpngrls'),
        'ndrsdfrc': fields.integer('ndrsdfrc'),
        'clrdfrc': fields.integer('clrdfrc'),
        'wtngc': fields.integer('wtngc'),
        'ndrsdttrvl': fields.integer('ndrsdttrvl'),
        'clrdfrtcktssnc': fields.integer('clrdfrtcktssnc'),
        'wtngtckt': fields.integer('wtngtckt'),
        'wtngflght': fields.integer('wtngflght'),
        'hstrvld': fields.integer('hstrvld'),
        'cnclld': fields.integer('cnclld'),
        'nfttwrk': fields.integer('nfttwrk'),    
        
        'colortotal': fields.integer('colortotal'),
        
        'colorprofile': fields.integer('Color Profile'),
        
        'reds': fields.char('Reds',  size=512),
        'current_action': fields.char('Current Action', size=768, readonly=True,),
        
        'create_date': fields.datetime('Create Date', readonly=True),
        'write_date': fields.datetime('Updated', readonly=True),
        'write_uid': fields.many2one('res.users', 'Updated by'),
        
        
        'trjob_id': fields.many2one('trjob', 'Job'),
        
        
        
        
        
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Photo",
            help="This field holds the image used as photo for the applicant, limited to 1024x1024px."),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized photo", type="binary", multi="_get_image",
            store = {
                'tapplicant': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized photo of the employee. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Smal-sized photo", type="binary", multi="_get_image",
            store = {
                'tapplicant': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized photo of the employee. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        
    }
    
    def _get_default_image(self, cr, uid, context=None):
        image_path = get_module_resource('hr', 'static/src/img', 'default_image.png')
        return tools.image_resize_image_big(open(image_path, 'rb').read().encode('base64'))
        
    
    _defaults = {
        'active': lambda *a: 1,
        'stage_id': lambda s, cr, uid, c: s._get_default_stage_id(cr, uid, c),
        'user_id': lambda s, cr, uid, c: uid,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
        'color': lambda *a: 0,
        'colortotal': lambda *a: 0,
        'colorprofile': lambda *a: 0,
        'current_action': lambda *b: 'frprflng',
        'image': _get_default_image,
        'date_last_stage_update': fields.datetime.now,
        
        
        
        'frprflng': 1,
        'tpdtchrgs': 0,
        'frdcmntcllctn': 0,
        'frmdcltst': 0,
        'mdclnprcss': 0,
        'fttwrk': 0,
        'frmdclpld': 0,
        'frgmctst': 0,
        'gmcnprcss': 0,
        'gmcfttwrk': 0,
        'frgmcpld': 0,
        'wtngmf': 0,
        'frvsrqst': 0,
        'wtngvsrls': 0,
        'nhldfrblncpymnts': 0,
        'nhldfrnncprtn': 0,
        'ndrsdfrhclrnc': 0,
        'vsxprd': 0,
        'vsrnwlnprcss': 0,
        'wtngvsrnwlrls': 0,
        'mdclxprd': 0,
        'frrmdcltst': 0,
        'wtngrmdclrls': 0,
        'ndrsdfrvsstmpng': 0,
        'clrdfrvsstmpng': 0,
        'vsstmpngnprcss': 0,
        'wtngvsstmpngrls': 0,
        'ndrsdfrc': 0,
        'clrdfrc': 0,
        'wtngc': 0,
        'ndrsdttrvl': 0,
        'clrdfrtcktssnc': 0,
        'wtngtckt': 0,
        'wtngflght': 0,
        'hstrvld': 0,
        'cnclld': 0,
        'nfttwrk': 0,    
        
        'colortotal': 0,
        
        
        
    }
    
    
    

    
    def write_exto(self, cr, uid, ids, vals, context=None):
        
        colortotal = 0
        
        for r in self.browse(cr, uid, ids, context=context):
            
            
            
            if (vals.get('user_email') or r.user_email) == False or (vals.get('gender') or r.gender) == False or (vals.get('date_birth') or r.date_birth) == False or (vals.get('homeaddress') or r.homeaddress) == False or ((vals.get('salary_basic') or r.salary_basic) == False and (vals.get('salary_gross') or r.salary_gross) == False):
                if r.frprflng == 0:
                    vals.update({'frprflng': 1}) 
                    colortotal += 1
            else:
                if r.frprflng > 0:
                    vals.update({'frprflng': 0})
            
            if (vals.get('hascv') or r.hascv) == '' or (vals.get('hasinterviewsheet')  or r.hasinterviewsheet) == False or (vals.get('haspassport') or r.haspassport) == False or (vals.get('hasoffersigned') or r.hasoffersigned) == False or (vals.get('hasphoto') or r.hasphoto) == False or (vals.get('formscompleted') or r.formscompleted) == False or (vals.get('nationality') or r.nationality) == False or (vals.get('passportnumber') or r.passportnumber) == False or (vals.get('passportexpiry') or r.passportexpiry) == False:
                if r.frdcmntcllctn == 0 and (vals.get('frprflng') or r.frprflng):
                    vals.update({'frdcmntcllctn': 1})
                    colortotal += 1
            else:
                if r.frdcmntcllctn > 0:
                    vals.update({'frdcmntcllctn': 0})
            
            
            if (vals.get('feeplacement') or r.feeplacement) == False or (vals.get('feeprocessing') or r.feeprocessing) == False:
                if r.tpdtchrgs == 0 and (vals.get('frprflng') or r.frprflng):
                    vals.update({'tpdtchrgs': 1})
                    colortotal += 1
            else:
                if r.tpdtchrgs > 0:
                    vals.update({'tpdtchrgs': 0})
                    
            if vals.get('medicalclinic') == '':
                vals.update({'medicalclinic': r.medicalclinic})
            
            
            
        
        vals.update({'colortotal': colortotal})
        
        
        #return super(tapplicant, self).write(cr, uid, ids, vals, context=context)
        
        return True
        
        
        
        
    def onchange_medicalclinic(self, cr, uid, ids, clinic, context = None):
        values = {'frmdcltst': 0 }
        if str(clinic).strip(' \t\n\r') != '':
            values['frmdcltst'] = 1
            
        return {'value': values}
    
    def onchange_gamcaclinic(self, cr, uid, ids, clinic, context = None):
        values = {'frgmctst': 0 }
        if clinic.strip(' \t\n\r') != '':
            values['frgmctst'] = 1
            
        return {'value': values}
    


        
    
        
        
tapplicant()




class tapplicant_sorted(osv.Model):
	_order = 'colortotal desc, id desc'
	_inherit = 'tapplicant'
    
tapplicant_sorted()



# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

