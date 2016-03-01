# -*- coding: utf-8 -*-

from openerp import models, fields, api

class mkjosms(models.Model):
    _name = 'mkjosms.mkjosms'

    name = fields.Char()
    stage_id = fields.selection((('draft', 'Draft'), ('queued', 'Queued'), ('done', 'Done')), 'Stage')
    message = fields.text('Message')
    boximport = fields.text('Recipients')
    tapplicant_ids = fields.Many2many('tapplicant')
    
    create_date = fields.datetime('Create Date', readonly=True)
    write_date = fields.datetime('Updated', readonly=True)
    write_uid = fields.many2one('res.users', 'Updated by', readonly=True)
    user_id = fields.many2one('res.users', 'Responsible')
    company_id = fields.many2one('res.company', 'Branch')
    
    
    