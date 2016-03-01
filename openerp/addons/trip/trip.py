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
    


trip()




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






# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
