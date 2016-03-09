# -*- encoding: utf-8 -*-

{
    'name': 'ACES Manpower Module',
    'version': '1.0',
    'category': 'HR',
    'summary': 'manpower pooling and job advertising',
    'description': """
Manpower pooling and Job advertising
================================

This module manages the testing
""",
    'depends' : ['base', 'testapi', 'web', 'hr','smsclient'],
    'data' : [
        'security/recruitment_security.xml',
        'security/ir.model.access.csv',
        'acesmanpower_view.xml',
        'acesmanpowerevent_view.xml',
        'acesmanpoweruser_view.xml',
        'acesmanpowerscreening_view.xml',
        'view/assets.xml',
        'wizard_view.xml',
        'acesmanpowerproperty_view.xml',
        'acesmanpowerjob_view.xml',
        'acesmanpowershortlist_view.xml',
        'dashboard_view.xml',
        'acesrecruitment_tool.xml',
        'website_add_terms_conditions.xml'
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
    
    ],
    'css': [
        '/acesmanpower/static/src/css/tripevents.css',
    
    ],     
    'images': [],
    'demo': [],
    'installable' : True,
    'application': True,
}
