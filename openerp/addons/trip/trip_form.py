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

class trip_form(osv.osv):
    _name = 'trip_form'
    _description = "Trip Form"
    _order = 'sequence'

    _columns = {
            'name': fields.char(size=256, string='Name', ),
            'description': fields.text(string='Description'  ),
            'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of forms."),
    }
    
    _defaults = {
        'sequence': 1,
    }


trip_form()



class trip_traveldoc(osv.osv):
    _name = 'trip_traveldoc'
    _description = "Trip Travel Documents"
    _order = 'sequence'

    _columns = {
            'name': fields.char(size=256, string='Name', ),
            'description': fields.text(string='Description'  ),
            'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of travel docs."),
    }
    
    _defaults = {
        'sequence': 1,
    }


trip_traveldoc()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
