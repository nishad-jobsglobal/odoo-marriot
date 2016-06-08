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
from openerp import api
from openerp import SUPERUSER_ID
from openerp.osv import osv, fields
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT

class trip_stage(osv.osv):
    """ Stage of Recruitment Trip """
    _name = "trip.stage"
    _description = "Stage of Recruitment Trip"
    _order = 'sequence'
    _columns = {
        'name': fields.char('Name', size=256, required=True, translate=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of stages."),        
        'template_id': fields.many2one('email.template', 'Use template', help="If set, a message is posted on the processor when the trip is set to the stage."),
        'fold': fields.boolean('Folded in Kanban View',
                               help='This stage is folded in the kanban view when'
                               'there are no records in that stage to display.'),
    }
    _defaults = {
        'sequence': 1,
    }

    

class trip(osv.osv):
    _name = 'trip'
    _description = "Trip"
    _order = "id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _get_default_stage_id(self, cr, uid, context=None):
        search_domain = []
        search_domain.append(('name', '=', 'Planning'))
        # perform search, return the first found
        stage_ids = self.pool.get('trip.stage').search(cr, uid, search_domain, context=context)
        if stage_ids:
            return stage_ids[0]
        return False
    
    _columns = {
        'name': fields.char(size=256, string='Name', required=True, ),
        'joblocation': fields.many2many('job_location', 'tri_jobloc_rel', 'trip_id', 'job_location_id', string='Job Locations',  ),
        'sourcinglocation': fields.many2many('sourcing_location', 'tri_solloc_rel', 'trip_id', 'sourcing_location_id', string='Sourcing Location', ),
        'stage_id': fields.many2one ('trip.stage', 'Stage', track_visibility='onchange'),
        'active': fields.boolean('Active',),
        'color': fields.integer('Color Index'),
        'company_id': fields.many2one('res.company', 'Branch'),
        'user_id': fields.many2one('res.users', 'Responsible', track_visibility='onchange'),
        'user_email': fields.related('user_id', 'email', type='char', string='User Email', readonly=True),
        'date_closed': fields.datetime('Closed', readonly=True, select=True),
        'date_open': fields.datetime('Assigned', readonly=True, select=True),
        'date_last_stage_update': fields.datetime('Last Stage Update', select=True),
        'date_action': fields.date('Next Action Date'),
        'title_action': fields.char('Next Action', size=64),
        'trip_start': fields.date('Date from'),
        'trip_end': fields.date('Date to'),
        'partner_id': fields.many2one('res.partner', 'Employer'),
        'description': fields.text('Description'),
        
        'triptype': fields.selection([('trip', 'Trip'),('skype', 'Skype'),('local', 'Local')], 'Type'),
        'visalen': fields.selection([(1, '1 month'),(2, '2 months'),(3, '3 months'),(4, 'above 3 months')], 'Visa Length'),
        'job_country_id': fields.many2one('res.country', 'Job Location'),
        'can_country_id': fields.many2one('res.country', 'Recruit Location'),
        
        
        'tapplicant_ids_level1': fields.one2many('tapplicant','trip_id','Level 1', domain=[('stage_id','<',2)], store=False ,readonly=True),
        'tapplicant_ids_level2': fields.one2many('tapplicant','trip_id','Level 2', domain=[('stage_id','=',2)], store=False ,readonly=True),
        'tapplicant_ids_level3': fields.one2many('tapplicant','trip_id','Level 3', domain=[('stage_id','=',3)], store=False ,readonly=True),
        'tapplicant_ids_level4': fields.one2many('tapplicant','trip_id','Level 4', domain=[('stage_id','=',4)], store=False ,readonly=True),
        'tapplicant_ids': fields.one2many('tapplicant','trip_id','Applicants'),
        
        'trjob_ids': fields.one2many('trjob','trip_id','Trip Jobs', store=True ,readonly=False),
        'importpid': fields.integer('Import Primary Key'), 
        
    }
    
    _defaults = {
        'active': lambda *a: 1,
        'stage_id': lambda s, cr, uid, c: s._get_default_stage_id(cr, uid, c),
        'user_id': lambda s, cr, uid, c: uid,
        'company_id': lambda s, cr, uid, c: s.pool.get('res.company')._company_default_get(cr, uid, 'hr.applicant', context=c),
        'color': 0,
        'date_last_stage_update': fields.datetime.now,
        'visalen': 3,
        'triptype': 'trip',
    }
    

    @api.model
    def create(self,vals):
        
        new_id = super(trip, self).create(vals)
        # Send SMS to the manager    
        resource_obj = self.env['resource.resource'].search([('user_id','=',self._uid)])
        self.env.cr.execute("SELECT id,name_related,coach_id FROM hr_employee WHERE resource_id="+str(resource_obj.id))
        rst = self.env.cr.fetchone()
        if rst not in (None,[None],[]):
            emp_id = rst[0] or False
            employee_name = rst[1] or ''
            coach_id = rst[2] or False
            
            if emp_id and coach_id:
                trip_obj = self.env['trip'].search([('id','=',new_id.id)])
                partner_name = trip_obj.partner_id.name or ''
                branch_location = trip_obj.company_id.name or ''
                self.env.cr.execute("SELECT mobile_phone FROM hr_employee WHERE id="+str(coach_id))
                rst = self.env.cr.fetchone()
                if rst not in (None,[None],[]):
                    coach_mobile = rst[0] or 0
                    thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
                    mess = 'Planned trip posted by '+ employee_name + ' for '+partner_name+' / '+branch_location
                    to = str(coach_mobile)
                    
                    ames={}
                    ames['msg'] = mess
                    ames['gateway_id'] = 1
                    ames['mobile'] = to
                    ames['name'] = thelink + "to=" + to + "&" + 'text=' + mess
                    created_id = self._uid or SUPERUSER_ID
                    self.pool.get('sms.smsclient.queue').create(self._cr,created_id,ames)
        return new_id
            
    @api.multi
    def write(self, values):
        stage_id = values.get('stage_id',False)
        trip_obj = self.env['trip'].search([('id','=',self.id)])
        resource_obj = self.env['resource.resource'].search([('user_id','=',self._uid)])
        self.env.cr.execute("SELECT id,name_related,coach_id FROM hr_employee WHERE resource_id="+str(resource_obj.id))
        rst = self.env.cr.fetchone()
        if rst not in (None,[None],[]):
            employee_name = rst[1] or ''
            coach_id = rst[2] or False
            partner_name = trip_obj.partner_id.name or ''
            branch_location = trip_obj.company_id.name or ''
            
            if coach_id and stage_id:
                self.env.cr.execute("SELECT mobile_phone FROM hr_employee WHERE id="+str(coach_id))
                rst = self.env.cr.fetchone()
                if rst not in (None,[None],[]):
                    coach_mobile = rst[0] or 0
                    trip_stage_obj = self.env['trip.stage'].search([('id','=',stage_id)])
                    tripstage = trip_stage_obj.name
                
                    thelink = "http://api.clickatell.com/http/sendmsg?password=YNZYHCMDTHaCDO&user=gagamba1&api_id=3502830&"
                    mess = partner_name+ ' trip '+tripstage+ ' by '+employee_name+ ' to '+branch_location
                    to = str(coach_mobile)
                    
                    ames={}
                    ames['msg'] = mess
                    ames['gateway_id'] = 1
                    ames['mobile'] = to
                    ames['name'] = thelink + "to=" + to + "&" + 'text=' + mess
                    created_id = self._uid or SUPERUSER_ID
                    self.pool.get('sms.smsclient.queue').create(self._cr,created_id,ames)
        return super(trip, self).write(values)


class res_partner(osv.osv):
    _inherit = 'res.partner'

    _columns = {
        'trip_id': fields.one2many('trip','partner_id','Trips', store=False ,readonly=True),
        'importpid': fields.integer('Import Primary Key'),
        'soacurrency_id': fields.many2one('res.currency', string='Currency'),
        'client': fields.boolean('Client', help="Check this box if this contact is a client."),
        'attachment_ids': fields.many2many('ir.attachment', 'class_ir_attachments_rel', 'class_id', 'attachment_id', 'Files'),
        'agreedfees': fields.text('Agreed Fees Summary'),
        'conterms': fields.text('Guarantee Terms Summary'),
        
        }

res_partner()

class res_users(osv.osv):
    _name = "res.users"
    _inherit = "res.users"
    _columns = {
                'callerid': fields.char('Caller ID', size=50,help="Caller ID used for the calls initiated by this user."),
                'internal_number': fields.char('Internal Number', size=15,help="User's internal phone number."),
                }


class recruitment_phonecall(osv.osv):
    
    """ Model for Recruitment phonecalls """
    _name = "recruitment.phonecall"
    _description = "Recruitment phonecalls"
    _order = "id desc"
    _inherit = ['mail.thread']
    
    _columns = {
        'create_date': fields.datetime('Creation Date' , readonly=True),
        'state': fields.selection(
            [('ANSWERED', 'Answered'),
             ('BUSY', 'Busy'),
             ('FAILED', 'Failed'),
             ('NO ANSWER', 'No Answer')
             ], string='Status', readonly=True, track_visibility='onchange',
            help='The status is set to Confirmed, when a case is created.\n'
                 'When the call is over, the status is set to Held.\n'
                 'If the call is not applicable anymore, the status can be set to Cancelled.'),
                
        'name': fields.char('Call Summary', required=True),
        'user_id': fields.many2one('res.users', 'Responsible'),
        'section_id': fields.many2one('crm.case.section', 'Sales Team', \
                        select=True, help='Sales team to which Case belongs to.'),
        'duration': fields.float('Duration', help='Duration in minutes and seconds.'),
        'partner_id': fields.many2one('res.partner', 'Contact'),
        'partner_phone': fields.char('Phone'),
        'partner_mobile': fields.char('Mobile'),
        'origin_phone': fields.char('Origin Phone'),
        'priority': fields.selection([('0','Low'), ('1','Normal'), ('2','High')], 'Priority'),
        'date': fields.datetime('Date'),
        'time': fields.float('Time'),
        'hour': fields.char('Hour'),
        'day':fields.integer('Day'),
        'month':fields.integer('Month'),
        'year':fields.integer('Year'),
        'company_id': fields.many2one('res.company', 'Company'),
        'description': fields.text('Description'),
        'nbr_cases': fields.integer('# of Cases', readonly=True),
    }
    
    def _get_default_state(self, cr, uid, context=None):
        if context and context.get('default_state'):
            return context.get('default_state')
        return 'open'

    _defaults = {
        'date': fields.datetime.now,
        'priority': '1',
        'state':  _get_default_state,
        'user_id': lambda self, cr, uid, ctx: uid,
    }
    
    def on_change_partner_id(self, cr, uid, ids, partner_id, context=None):
        values = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            values = {
                'partner_phone': partner.phone,
                'partner_mobile': partner.mobile,
            }
        return {'value': values}
    
    def compute_duration(self, cr, uid, ids, context=None):
        for phonecall in self.browse(cr, uid, ids, context=context):
            if phonecall.duration <= 0:
                duration = datetime.now() - datetime.strptime(phonecall.date, DEFAULT_SERVER_DATETIME_FORMAT)
                values = {'duration': duration.seconds/float(60)}
                self.write(cr, uid, [phonecall.id], values, context=context)
        return True






# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
