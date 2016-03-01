# -*- coding: utf-8 -*-

from openerp import models, fields, api

class mkjolog(models.Model):
    _inherit = "auditlog.log"

    @api.one
    @api.depends("line_ids")
    def _field_count(self):
        total = 0
        for line in self.line_ids:
            total = total + 1
        
        self.field_count = total
    
    
    field_count = fields.Integer(compute="_field_count", store=True, string="Fields Updated")
    
    

    
