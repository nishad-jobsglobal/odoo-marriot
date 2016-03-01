# -*- coding: utf-8 -*-
{
    'name': 'MK JO MA SMS',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'sms mass messaging',
    'description': """
SMS, Notifications, Updates
================================

This module manages the sms messaging of candidates together with notifications
""",
    'depends' : ['base', 'hr'],
    'data' : [
        'security/ir.model.access.csv',
        'mkjosms_view.xml',
    ],
    'images': [],
    'demo': [],
    'installable' : True,
    'application': True,
}