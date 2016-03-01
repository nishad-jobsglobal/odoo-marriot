# -*- encoding: utf-8 -*-

{
    'name': 'Test Widget',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'widget testing purposes',
    'description': """
Tesing lang to
================================

This module manages the testing of widgets
""",
    'depends' : ['base'],
    'data' : [
        'testwidget_view.xml',
    ],
    'images': [],
    'demo': [],
    'js': [
        'static/js/testwidget.js',
    ],
    'css': [
        'static/testwidget.css',
    ],
    'qweb': [
        'static/xml/testwidget.xml',
    ],
    'installable' : True,
    'application': True,
}
