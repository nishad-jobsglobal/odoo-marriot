# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

{
    'name': 'Recruitment Trip',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'trips, candidate tracking and deployment',
    'description': """
Trips, Applicants, Deployment
================================

This module manages the trips, applicants,
tracking, and the deployment of candidates.
""",
    'depends' : ['base', 'hr', 'hr_recruitment'],
    'data' : [
        'security/ir.model.access.csv',
        'trip_view.xml',
        'job_location_view.xml',
        'sourcing_location_view.xml',
        'tapplicant_view.xml',
        'trip_form_view.xml',
        'menu/tapp_profiling.xml',
        'menu/tapp_medical.xml',
        'menu/tapp_visa.xml',
        'menu/tapp_travel.xml',
        'menu/tapp_account.xml',
        'tviews/trjob_view.xml',
        'security/security.xml',
        'security/security.xml',
    ],
    'images': [],
    'demo': [],
    'installable' : True,
    'application': True,
}
