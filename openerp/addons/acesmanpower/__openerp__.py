# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Jobsglobal.com
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
##############################################################################

{
    'name': 'ACES Manpower Module',
    'version': '1.0',
    'category': 'HR',
    'summary': 'Manpower pooling and job advertising',
    'description': """
Manpower pooling and Job advertising
====================================

This module manages the testing
""",
    'depends' : ['base','web', 'hr','smsclient','trip','edi'],
    'data' : [
        'security/recruitment_security.xml',
        'security/ir.model.access.csv',
        'view/assets.xml',
        'wizard_view.xml',
        'acesmanpower_view.xml',
        'acesmanpowerevent_view.xml',
        'acesmanpoweruser_view.xml',
        'acesmanpowerscreening_view.xml',
        'acesmanpowerproperty_view.xml',
        'acesmanpowerjob_view.xml',
        'acesmanpowershortlist_view.xml',
        'dashboard_view.xml',
        'acesrecruitment_tool.xml',
        'website_add_terms_conditions.xml',
        'trip_view.xml',
        'tapplicant_view.xml',
        'acesrelationship_view.xml',
        'edi/property_action_data.xml',
        'menu_view.xml',
    ],
     'js': [
        'static/src/js/resource.js',
        'static/src/js/tripevents.js',
        'static/src/adminlte/js/plugins/jquery-jvectormap-usa-en.js',
        'static/src/adminlte/js/plugins/jquery-jvectormap-world-mill-en.js',
        
     ],
    'qweb': [
        'static/src/xml/resource.xml',
        'static/src/xml/dashboard.xml',
        'static/src/xml/upload.xml',
    
    ],
    'css': [
        '/acesmanpower/static/src/css/tripevents.css',
    
    ],     
    'images': [],
    'demo': [],
    'installable' : True,
    'application': True,
    'auto_install': False,
}
