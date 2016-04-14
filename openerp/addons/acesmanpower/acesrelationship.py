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
from openerp.osv import osv, fields
from openerp.tools.translate import _
from openerp import tools

class work_experience(osv.osv):
    _name = 'work.experience'
    _description = "Work Experience"
    
    _columns = {
                'referral_id':fields.many2one('manpower.referral'),
                'employer_name': fields.char("Name of Employer"),
                'job_title':fields.char('Job Title'),
                'start_date':fields.date("Start Date"),
                'end_date':fields.date("End Date"),
                }

class education_qualification(osv.osv):
    _name = 'education.qualification'
    _description = "Education Qualification"
    
    _columns = {
                'referral_id':fields.many2one('manpower.referral'),
                'highest_qualification': fields.char("Highest qualification"),
                'institute':fields.char('Institute'),
                'end_date':fields.date("End Date"),
                }
    
class skills(osv.osv):
    _name = 'skills'
    _description = "Skills"
    _order = "id desc" 
    _columns ={
               'name' : fields.char("Name")
               }
    
class joined_activities(osv.osv):
    _name = 'joined.activities'
    _description = "Joined Activities"
    _order = "id desc" 
    _columns ={
               'referral_id':fields.many2one('manpower.referral'),
               'date' : fields.datetime("Date"),
               'description':fields.text("Description")
               }
    
    
class calendar_event(osv.Model):
    """ Model for Calendar Event """
    _inherit = 'calendar.event'
    _columns = {
        'referrals_id': fields.many2one('manpower.referral', 'Referral'),
    }


class manpower_referral(osv.osv):
    _name = 'manpower.referral'
    _description = "Manpower Referral"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    
    def _meeting_count(self, cr, uid, ids, field_name, arg, context=None):
        event = self.pool['calendar.event']
        return {
            ref_id: event.search_count(cr,uid, [('referrals_id', '=', ref_id)], context=context)
            for ref_id in ids
        }
    
    _columns = {
                'name': fields.char("Name"),
                'no_cv':fields.boolean('No CV'),
                'first_name':fields.char("First Name"),
                'sur_name':fields.char("Sur Name"),
                'age':fields.integer("Age"),
                'location':fields.char("Location"),
                'nationality':fields.many2one('res.country',string="Nationality"),
                'position_referred':fields.char("Position preferred"), # TO CHANGE
                'current_position':fields.char("Current Position"), # TO CHANGE
                'work_experience_ids':fields.one2many('work.experience','referral_id', "Work Experience"),
                'education_ids':fields.one2many('education.qualification','referral_id', "Education"),
                'activity_ids':fields.one2many('joined.activities','referral_id', "Joined Activities"),
                'skill_ids':fields.many2many('skills','referral_skills_rel','skill_id','masterskills_id',"Skills"),
                'contact_date':fields.datetime("Contact Date"),
                'user_id': fields.many2one('res.users', 'User'),
                'meeting_count': fields.function(_meeting_count, string='# Meetings', type='integer'),
                }
    
    _defaults = {
        'user_id': lambda s, cr, uid, c: uid,
    }
    
    @api.multi
    def action_upload_cv(self):
        res = {
               'type': 'ir.actions.client',
               'name':'Upload CV',
               'tag':'acesmanpower.uploadpage',
        }
        return res
    
    @api.multi
    def send_email(self):
        return True
    
    def schedule_meeting(self, cr, uid, ids, context=None):
        """
        Open meeting's calendar view to schedule meeting on current referral.
        :return dict: dictionary value for created Meeting view
        """
        referral = self.browse(cr, uid, ids[0], context)
        res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid, 'calendar', 'action_calendar_event', context)
        partner_ids = [self.pool['res.users'].browse(cr, uid, uid, context=context).partner_id.id]
        if referral.user_id.partner_id:
            partner_ids.append(referral.user_id.partner_id.id)
        res['context'] = {
            'search_default_referrals_id': referral.id or False,
            'default_referrals_id': referral.id or False,
            'default_partner_id': referral.user_id.partner_id and referral.user_id.partner_id.id or False,
            'default_name': referral.first_name
        }
        return res
    
    def joined_activity(self, cr, uid, ids, context=None):
        models_data = self.pool.get('ir.model.data')
        ids = self.browse(cr, uid, ids, context=context)[0]
        # Get opportunity views
        dummy, form_view = models_data.get_object_reference(cr, uid, 'acesmanpower', 'view_manpower_referral_activities_form')
        dummy, tree_view = models_data.get_object_reference(cr, uid, 'acesmanpower', 'view_manpower_referral_activities_tree')
        return {
            'name': _('Joined Activities'),
            'view_type': 'tree',
            'view_mode': 'tree,form',
            'res_model': 'joined.activities',
            'res_id': int(ids),
            'view_id': False,
            'views': [(tree_view or False, 'tree'),(form_view or False, 'form')],
            'type': 'ir.actions.act_window',
            'context': {}
        }
        
class referral_analysis_report(osv.Model):
    """ Referral Analysis """
    _name = "referral.analysis.report"
    _auto = False
    _description = "Referral Analysis"

    _columns = {
        'create_date': fields.datetime('Creation Date', readonly=True),
        'nbr_cases': fields.integer("# of Cases", readonly=True),
        'user_id':fields.many2one('res.users', 'User', readonly=True),
        'join_id':fields.many2one('joined.activities','Activity',readonly=True),
        'total_activities': fields.integer("# of Activities", readonly=True),
        'first_name':fields.related('manpower.referral.first_name'),
    }

    def init(self, cr):

        """
            Referral Analysis Report
            @param cr: the current row, from the database cursor
        """
        tools.drop_view_if_exists(cr, 'referral_analysis_report')
        cr.execute("""
            CREATE OR REPLACE VIEW referral_analysis_report AS (
                SELECT
                    m.id,
                    count(m.id) as nbr_cases,
                    m.user_id,
                    m.first_name as first_name,
                    m.contact_date as create_date,
                    (select count(*) from joined_activities where joined_activities.referral_id = m.id) as total_activities,
                    count(j.referral_id) as activities
                FROM
                    manpower_referral m
                INNER JOIN joined_activities j
                ON j.referral_id = m.id
                GROUP BY m.id,m.user_id
            )""")

    
class manpower_referral_line(osv.osv):
    _name = 'manpower.referral.line'
    _description = "Manpower Referral Details"
    