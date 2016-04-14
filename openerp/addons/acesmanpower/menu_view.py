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
from openerp.tools.translate import _

class res_company(osv.osv):
    _inherit = 'res.company'
    _name = 'res.company'
    
    _columns = {
                'groups_id': fields.many2many('res.groups', 'res_company_groups_rel', 'cid', 'gid', 'Access Groups'),
                }
    
class res_users(osv.osv):
    _inherit = 'res.users'
    _name = 'res.users'
    _description = "Users"
    
    
    def fields_get(self, cr, uid, allfields=None, context=None, write_access=True, attributes=None):
        # uid is SUPERUSER_ID, so we need to change it
        #uid = self.pool['ir.config_parameter'].get_param(cr, uid, IR_CONFIG_NAME, context=context)
        
        if uid != 1:
            uid = 1
        ctx = (context or {}).copy()    
        return super(res_users, self).fields_get(cr, uid, allfields=allfields, context=ctx, write_access=write_access, attributes=attributes)

