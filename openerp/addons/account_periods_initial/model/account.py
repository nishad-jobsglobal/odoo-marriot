#!/usr/bin/python
# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# Credits######################################################
#    Coded by: Juan Carlos Funes(juan@vauxoo.com)
#############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
##########################################################################

from openerp.osv import osv


class account_period(osv.Model):
    _inherit = "account.period"

    def build_ctx_periods_initial(self, cr, uid, period_to_id):
        period_to = self.browse(cr, uid, period_to_id)
        period_date_start = period_to.date_start
        company_id = period_to.company_id.id
        fiscalyear_id = period_to.fiscalyear_id.id
        return self.search(cr, uid, [('date_stop', '<=', period_date_start),
                                     ('company_id', '=', company_id),
                                     ('id', '<>', period_to_id),
                                     ('fiscalyear_id', '=', fiscalyear_id)])
        # Falta validar cuando el period_to_id es special, ya que puede tomar
        # enero cuando no es necesario.
